"""
SQLAlchemy ORM Models for CareQueue.

This module defines the database schema for the CareQueue application:
- Clinic: Represents medical clinics
- Doctor: Represents doctors associated with clinics
- Patient: Represents patients who can join queues
- Token: Represents queue tokens for patient-doctor appointments

Relationships:
- One Clinic has many Doctors (one-to-many)
- One Doctor has many Tokens (one-to-many)
- One Patient can have many Tokens (one-to-many)
"""

from database import db
from datetime import datetime
from sqlalchemy import func
import bcrypt


class Clinic(db.Model):
    """
    Clinic model representing medical facilities.
    
    Attributes:
        id: Primary key
        name: Clinic name (e.g., "Vital Wave Rehabs")
        location: Clinic address/location
        doctors: Relationship to Doctor model (one-to-many)
    """
    __tablename__ = 'clinics'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(500), nullable=False)
    maps_link = db.Column(db.String(1000), nullable=True)  # Google Maps share link

    # Relationship: One clinic has many doctors
    # cascade='all, delete-orphan' ensures when a clinic is deleted, its doctors are too
    doctors = db.relationship('Doctor', backref='clinic', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert clinic to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'maps_link': self.maps_link or ''
        }
    
    def __repr__(self):
        return f'<Clinic {self.name}>'


class Doctor(db.Model):
    """
    Doctor model representing medical practitioners.
    
    Attributes:
        id: Primary key
        name: Doctor's name
        licence_number: Unique licence number for login (e.g., "GJ1334")
        specialization: Medical specialization
        clinic_id: Foreign key to Clinic
        opd_start_time: OPD start time (e.g., "09:00")
        opd_end_time: OPD end time (e.g., "17:00")
        status: Manual status toggle - "Open", "Break", "Closed"
        current_token_number: The token number currently being served
        api_key: Unique API key for authentication
        tokens: Relationship to Token model (one-to-many)
    """
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    specialization = db.Column(db.String(200), nullable=False)
    
    # Licence number: Unique identifier for doctor login
    licence_number = db.Column(db.String(20), unique=True, nullable=True)
    
    # Foreign Key: Links doctor to a clinic
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.id'), nullable=False)
    
    # OPD Timing: Operating hours for the doctor
    opd_start_time = db.Column(db.String(10), nullable=False, default="09:00")
    opd_end_time = db.Column(db.String(10), nullable=False, default="12:00")
    
    # Status: Manual toggle by doctor - "Open", "Break", "Closed"
    status = db.Column(db.String(20), nullable=False, default="Closed")
    
    # Current token number being served (incremented by Mark Done)
    current_token_number = db.Column(db.Integer, nullable=False, default=0)
    
    # API Key: Unique authentication token for doctor actions
    api_key = db.Column(db.String(100), unique=True, nullable=False)
    
    # Password hash: bcrypt hash of the 4-digit PIN.
    # Nullable=True for backward compatibility with existing records.
    # Doctors without a hash will be prompted to set one on first login.
    password_hash = db.Column(db.String(255), nullable=True)

    # Relationship: One doctor has many tokens
    # cascade='all, delete-orphan' ensures tokens are deleted when doctor is deleted
    tokens = db.relationship('Token', backref='doctor', lazy=True, cascade='all, delete-orphan')
    
    # -------------------------------------------------------------------------
    # Password helpers
    # -------------------------------------------------------------------------
    
    def set_password(self, pin: str) -> None:
        """
        Hash and store a 4-digit PIN using bcrypt.
        
        Args:
            pin: Exactly 4 numeric digits as a string, e.g. "1234"
        """
        pin_bytes = pin.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        self.password_hash = bcrypt.hashpw(pin_bytes, salt).decode('utf-8')
    
    def check_password(self, pin: str) -> bool:
        """
        Verify a PIN against the stored bcrypt hash.
        
        Args:
            pin: The raw PIN string to check
            
        Returns:
            True if the PIN matches, False otherwise
        """
        if not self.password_hash:
            return False
        return bcrypt.checkpw(pin.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def has_password(self) -> bool:
        """Return True if a password has been set for this doctor."""
        return self.password_hash is not None

    def get_effective_status(self):
        """
        Get effective status considering both manual status and OPD timing.
        
        Doctor manual toggle 'Open' can override OPD hours (so they can open early).
        If not explicitly 'Open', defaults to 'Closed' outside OPD hours.
        """
        now = datetime.now().strftime("%H:%M")
        
        # Always respect manual "Open" override so doctor can open before OPD time
        if self.status == "Open":
            return "Open"
            
        # If outside OPD hours and not explicitly opened, default to Closed
        if now < self.opd_start_time or now > self.opd_end_time:
            return "Closed"
        
        # During OPD hours, use manual status
        return self.status

    def is_open(self):
        """
        Check if the doctor is currently accepting patients.
        Returns: True if effective status is "Open".
        """
        return self.get_effective_status() == "Open"
    
    def get_current_token(self):
        """
        Get the currently active (serving) token for this doctor.
        
        Returns:
            Token object or None if no waiting tokens exist
        """
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        return Token.query.filter(
            Token.doctor_id == self.id,
            Token.status == 'waiting',
            Token.created_at >= today_start
        ).order_by(Token.created_at.asc()).first()
    
    def get_waiting_count(self):
        """
        Get the number of patients waiting in queue today.
        
        Returns:
            Integer count of waiting tokens
        """
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        return Token.query.filter(
            Token.doctor_id == self.id,
            Token.status == 'waiting',
            Token.created_at >= today_start
        ).count()
    
    def get_waiting_tokens(self):
        """
        Get all waiting tokens for this doctor today (ordered by token number).
        
        Returns:
            List of Token objects
        """
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        return Token.query.filter(
            Token.doctor_id == self.id,
            Token.status == 'waiting',
            Token.created_at >= today_start
        ).order_by(Token.token_number.asc()).all()
    
    def get_next_token_number(self):
        """
        Calculate the next token number for this doctor today.
        
        Returns:
            Integer token number (auto-increments per doctor per day)
        """
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        max_token = db.session.query(func.max(Token.token_number)).filter(
            Token.doctor_id == self.id,
            Token.created_at >= today_start
        ).scalar()
        
        return (max_token or 0) + 1
    
    def get_average_consultation_time(self):
        """
        Calculate average consultation time in minutes based on served tokens today.
        
        Measures time between consecutive served_at timestamps.
        
        Returns:
            Float average minutes, or 5.0 as default if insufficient data
        """
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        served_tokens = Token.query.filter(
            Token.doctor_id == self.id,
            Token.status == 'served',
            Token.served_at.isnot(None),
            Token.created_at >= today_start
        ).order_by(Token.served_at.asc()).all()
        
        if len(served_tokens) < 2:
            return 5.0  # Default 5 minutes if not enough data
        
        # Calculate time differences between consecutive served_at timestamps
        total_diff = 0
        count = 0
        for i in range(1, len(served_tokens)):
            diff = (served_tokens[i].served_at - served_tokens[i-1].served_at).total_seconds() / 60.0
            if diff > 0 and diff < 60:  # Ignore outliers > 60 min
                total_diff += diff
                count += 1
        
        if count == 0:
            return 5.0
        
        return round(total_diff / count, 1)
    
    def to_dict(self, include_stats=False):
        """
        Convert doctor to dictionary for JSON serialization.
        
        Args:
            include_stats: If True, include queue statistics
            
        Returns:
            Dictionary representation of doctor
        """
        data = {
            'id': self.id,
            'name': self.name,
            'specialization': self.specialization,
            'licence_number': self.licence_number,
            'clinic_id': self.clinic_id,
            'opd_start_time': self.opd_start_time,
            'opd_end_time': self.opd_end_time
        }
        
        if include_stats:
            effective_status = self.get_effective_status()
            current_token = self.current_token_number
            waiting_count = self.get_waiting_count()
            avg_time = self.get_average_consultation_time()
            
            data['current_token'] = f"#{current_token}" if current_token > 0 else "NA"
            data['current_token_number'] = current_token
            data['waiting_count'] = waiting_count
            data['is_open'] = effective_status == "Open"
            data['status'] = effective_status
            data['average_consultation_time'] = avg_time
        
        return data
    
    def __repr__(self):
        return f'<Doctor {self.name}>'


class Patient(db.Model):
    """
    Patient model representing patients who use the queue system.
    
    Attributes:
        id: Primary key
        name: Patient's name
        phone_number: Unique 10-digit phone number (used for login)
        password_hash: bcrypt hash of the 4-digit PIN (never stored as plain text)
        tokens: Relationship to Token model (one-to-many)
    """
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    
    # Phone number is unique and used for patient identification/login
    phone_number = db.Column(db.String(10), unique=True, nullable=False)
    
    # Password hash: bcrypt hash of the 4-digit PIN.
    # Nullable=True for backward compatibility with existing records.
    # Patients without a hash will be prompted to set one on first login.
    password_hash = db.Column(db.String(255), nullable=True)
    
    # Relationship: One patient can have many tokens
    tokens = db.relationship('Token', backref='patient', lazy=True)
    
    # -------------------------------------------------------------------------
    # Password helpers
    # -------------------------------------------------------------------------
    
    def set_password(self, pin: str) -> None:
        """
        Hash and store a 4-digit PIN using bcrypt.
        
        Args:
            pin: Exactly 4 numeric digits as a string, e.g. "1234"
        """
        pin_bytes = pin.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        self.password_hash = bcrypt.hashpw(pin_bytes, salt).decode('utf-8')
    
    def check_password(self, pin: str) -> bool:
        """
        Verify a PIN against the stored bcrypt hash.
        
        Args:
            pin: The raw PIN string to check
            
        Returns:
            True if the PIN matches, False otherwise
        """
        if not self.password_hash:
            return False
        return bcrypt.checkpw(pin.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def has_password(self) -> bool:
        """Return True if a password has been set for this patient."""
        return self.password_hash is not None
    
    def to_dict(self):
        """Convert patient to dictionary for JSON serialization.
        
        NOTE: password_hash is intentionally excluded from the response.
        """
        return {
            'id': self.id,
            'name': self.name,
            'phone_number': self.phone_number,
            'has_password': self.has_password()
        }
    
    def __repr__(self):
        return f'<Patient {self.name} - {self.phone_number}>'



class Token(db.Model):
    """
    Token model representing queue positions.
    
    Attributes:
        id: Primary key
        patient_id: Foreign key to Patient
        doctor_id: Foreign key to Doctor
        token_number: Auto-incremented number per doctor per day
        status: Current status ('waiting', 'served', 'cancelled')
        created_at: Timestamp when token was created
        served_at: Timestamp when doctor marked token as done
    """
    __tablename__ = 'tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    
    # Token number: Auto-incremented per doctor per day
    token_number = db.Column(db.Integer, nullable=False)
    
    # Status: 'waiting', 'served', 'cancelled'
    status = db.Column(db.String(20), nullable=False, default='waiting')
    
    # Timestamp: When the token was created
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    
    # Timestamp: When the doctor marked this token as done
    served_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        """Convert token to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.name if self.patient else None,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.name if self.doctor else None,
            'token_number': self.token_number,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'served_at': self.served_at.isoformat() if self.served_at else None
        }
    
    def __repr__(self):
        return f'<Token #{self.token_number} - Doctor {self.doctor_id} - {self.status}>'
