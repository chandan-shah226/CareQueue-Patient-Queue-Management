"""
Doctor-related API endpoints for CareQueue.

Endpoints:
- POST /api/doctor/login - Login with licence number
- POST /api/doctor/register - Register new doctor
- GET /api/doctor/dashboard/<doctor_id> - Get dashboard data
- POST /api/doctor/mark_done - Mark current patient as done
- POST /api/doctor/update_status - Change OPD status
- POST /api/doctor/reset_queue - Reset queue
- GET /api/current_token/<doctor_id> - Get current active token
- GET /api/doctor_queue/<doctor_id> - Get all waiting tokens
"""

from flask import Blueprint, request, jsonify
from database import db
from models import Doctor, Token, Clinic
from datetime import datetime
import secrets
import re
import time
from collections import defaultdict

# ── Blueprint ──────────────────────────────────────────────────────────────────
doctor_bp = Blueprint('doctor', __name__, url_prefix='/api')

# ── Rate-limit store (in-memory dictionary) ────────────────────────────────────
_login_attempts: dict = defaultdict(list)
MAX_ATTEMPTS = 5         
WINDOW_SECONDS = 60      

def _is_rate_limited(ip: str) -> bool:
    now = time.time()
    _login_attempts[ip] = [t for t in _login_attempts[ip] if now - t < WINDOW_SECONDS]
    return len(_login_attempts[ip]) >= MAX_ATTEMPTS

def _record_failed_attempt(ip: str) -> None:
    _login_attempts[ip].append(time.time())

def _validate_pin(pin: str) -> tuple[bool, str]:
    if not pin:
        return False, "PIN is required"
    if not re.fullmatch(r'\d{4}', pin):
        return False, "PIN must be exactly 4 digits (numbers only)"
    return True, ''

@doctor_bp.route('/doctor/check', methods=['POST'])
def check_doctor():
    """
    Check if a doctor license exists and if it has a password set.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    licence = data.get('licence_number', '').strip().upper()
    doctor = Doctor.query.filter_by(licence_number=licence).first()
    
    if not doctor:
        return jsonify({'exists': False, 'has_password': False}), 200

    return jsonify({
        'exists': True,
        'has_password': doctor.has_password(),
        'name': doctor.name
    }), 200

@doctor_bp.route('/doctor/set_pin', methods=['POST'])
def set_doctor_pin():
    """
    Set a 4-digit PIN for an EXISTING doctor who does not yet have one.
    """
    ip = request.remote_addr or '127.0.0.1'
    if _is_rate_limited(ip):
        return jsonify({'error': 'Too many attempts', 'message': 'Please wait 1 minute.'}), 429

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    licence = data.get('licence_number', '').strip().upper()
    pin = str(data.get('pin', '')).strip()

    pin_ok, pin_msg = _validate_pin(pin)
    if not pin_ok:
        return jsonify({'error': 'Invalid PIN format', 'message': pin_msg}), 400

    doctor = Doctor.query.filter_by(licence_number=licence).first()
    if not doctor:
        _record_failed_attempt(ip)
        return jsonify({'error': 'Doctor not found', 'message': 'Not registered.'}), 404

    if doctor.has_password():
        return jsonify({'error': 'PIN already set', 'message': 'Please log in.'}), 409

    doctor.set_password(pin)
    db.session.commit()
    _login_attempts.pop(ip, None)

    return jsonify({
        'message': 'PIN set successfully',
        'doctor': doctor.to_dict(include_stats=True),
        'api_key': doctor.api_key
    }), 200

@doctor_bp.route('/doctor/login', methods=['POST'])
def doctor_login():
    """
    Login doctor by licence number.
    
    Request Body (JSON):
        { "licence_number": "GJ1334" }
    
    Response:
        Found (200): { "doctor": {...}, "message": "Login successful" }
        Not Found (404): { "error": "Doctor not found" }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
        
    ip = request.remote_addr or '127.0.0.1'
    if _is_rate_limited(ip):
        return jsonify({'error': 'Too many attempts', 'message': 'Please wait 1 minute.'}), 429
    
    if 'licence_number' not in data or 'pin' not in data:
        return jsonify({'error': 'Licence number and PIN are required'}), 400
    
    licence = data['licence_number'].strip().upper()
    pin = str(data['pin']).strip()
    
    pin_ok, pin_msg = _validate_pin(pin)
    if not pin_ok:
        return jsonify({'error': 'Invalid PIN format', 'message': pin_msg}), 400
    
    doctor = Doctor.query.filter_by(licence_number=licence).first()
    
    if not doctor:
        _record_failed_attempt(ip)
        return jsonify({
            'error': 'Doctor not found',
            'message': 'No doctor registered with this licence number'
        }), 404
        
    if not doctor.has_password():
        return jsonify({
            'error': 'No PIN set',
            'message': 'Please set your PIN first.'
        }), 400
        
    if not doctor.check_password(pin):
        _record_failed_attempt(ip)
        return jsonify({
            'error': 'Incorrect PIN',
            'message': 'The PIN you entered is incorrect.'
        }), 401
    
    _login_attempts.pop(ip, None)
    
    return jsonify({
        'message': 'Login successful',
        'doctor': doctor.to_dict(include_stats=True),
        'api_key': doctor.api_key
    }), 200


@doctor_bp.route('/doctor/register', methods=['POST'])
def doctor_register():
    """
    Register a new doctor and their clinic.
    
    Request Body (JSON):
        {
            "licence_number": "GJ1334",
            "name": "Dr. Hetvi Rathod",
            "clinic_name": "Vital Wave Rehabs",
            "clinic_address": "Jamnagar",
            "specialization": "Physiotherapy",
            "opd_start": "11:00",
            "opd_end": "17:00"
        }
    
    Response:
        Success (201): { "doctor": {...}, "api_key": "..." }
        Duplicate (409): { "error": "Doctor already registered" }
    """
    data = request.get_json(silent=True)
    
    required_fields = ['licence_number', 'name', 'clinic_name', 'clinic_address', 
                       'specialization', 'opd_start', 'opd_end', 'pin']
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    missing = [f for f in required_fields if f not in data or not str(data[f]).strip()]
    if missing:
        return jsonify({
            'error': 'Missing required fields',
            'missing': missing
        }), 400
    
    licence = data['licence_number'].strip().upper()
    pin = str(data['pin']).strip()
    
    pin_ok, pin_msg = _validate_pin(pin)
    if not pin_ok:
        return jsonify({'error': 'Invalid PIN format', 'message': pin_msg}), 400
    
    # Check if doctor already exists
    existing = Doctor.query.filter_by(licence_number=licence).first()
    if existing:
        return jsonify({
            'error': 'Doctor already registered',
            'message': 'A doctor with this licence number already exists'
        }), 409
    
    try:
        # Find or create clinic
        clinic = Clinic.query.filter_by(
            name=data['clinic_name'].strip()
        ).first()
        
        if not clinic:
            clinic = Clinic(
                name=data['clinic_name'].strip(),
                location=data['clinic_address'].strip()
            )
            db.session.add(clinic)
            db.session.flush()  # Get the clinic ID
        
        # Generate API key
        api_key = secrets.token_urlsafe(32)
        
        # Create doctor
        doctor = Doctor(
            name=data['name'].strip(),
            licence_number=licence,
            specialization=data['specialization'].strip(),
            clinic_id=clinic.id,
            opd_start_time=data['opd_start'].strip(),
            opd_end_time=data['opd_end'].strip(),
            status='Closed',
            current_token_number=0,
            api_key=api_key
        )
        doctor.set_password(pin)
        
        db.session.add(doctor)
        db.session.commit()
        
        return jsonify({
            'message': 'Doctor registered successfully',
            'doctor': doctor.to_dict(include_stats=True),
            'api_key': api_key
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@doctor_bp.route('/doctor/dashboard/<int:doctor_id>', methods=['GET'])
def doctor_dashboard(doctor_id):
    """
    Get full dashboard data for a doctor.
    
    Returns doctor info, current token, waiting count, waiting token list
    (token numbers only for privacy), and average consultation time.
    """
    doctor = Doctor.query.get(doctor_id)
    
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404
    
    # Get waiting tokens (numbers only - no patient names for privacy)
    waiting_tokens = doctor.get_waiting_tokens()
    waiting_token_numbers = [t.token_number for t in waiting_tokens]
    
    # Get average consultation time
    avg_time = doctor.get_average_consultation_time()
    
    # Get clinic info
    clinic = Clinic.query.get(doctor.clinic_id)
    
    return jsonify({
        'doctor': {
            'id': doctor.id,
            'name': doctor.name,
            'licence_number': doctor.licence_number,
            'specialization': doctor.specialization
        },
        'clinic': {
            'id': clinic.id,
            'name': clinic.name,
            'location': clinic.location
        },
        'opd_start_time': doctor.opd_start_time,
        'opd_end_time': doctor.opd_end_time,
        'status': doctor.get_effective_status(),
        'current_token_number': doctor.current_token_number,
        'waiting_count': doctor.get_waiting_count(),
        'waiting_tokens': waiting_token_numbers,
        'average_consultation_time': avg_time
    }), 200


@doctor_bp.route('/doctor/mark_done', methods=['POST'])
def mark_done():
    """
    Mark the current (oldest waiting) token as served.
    
    Request Body (JSON):
        { "doctor_id": 1 }
    
    Logic:
    - Finds oldest waiting token for today
    - Sets status to 'served' and records served_at timestamp
    - Increments doctor's current_token_number
    - Returns updated dashboard state
    """
    data = request.get_json()
    
    if not data or 'doctor_id' not in data:
        return jsonify({'error': 'doctor_id is required'}), 400
    
    doctor = Doctor.query.get(data['doctor_id'])
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404
    
    if doctor.get_effective_status() != "Open":
        return jsonify({
            'error': 'Cannot mark done',
            'message': 'OPD is not currently open'
        }), 400
    
    # Get the oldest waiting token
    current_token = doctor.get_current_token()
    
    if not current_token:
        return jsonify({
            'error': 'No patients waiting',
            'message': 'Queue is empty'
        }), 400
    
    try:
        # Mark token as served
        current_token.status = 'served'
        current_token.served_at = datetime.now()
        
        # Update doctor's current token number
        doctor.current_token_number = current_token.token_number
        
        db.session.commit()
        
        # Get updated state
        next_token = doctor.get_current_token()
        waiting_count = doctor.get_waiting_count()
        waiting_tokens = [t.token_number for t in doctor.get_waiting_tokens()]
        avg_time = doctor.get_average_consultation_time()
        
        return jsonify({
            'message': 'Patient marked as done',
            'served_token': current_token.token_number,
            'current_token_number': doctor.current_token_number,
            'next_token': next_token.token_number if next_token else None,
            'waiting_count': waiting_count,
            'waiting_tokens': waiting_tokens,
            'average_consultation_time': avg_time
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@doctor_bp.route('/doctor/update_status', methods=['POST'])
def update_status():
    """
    Update doctor's OPD status.
    
    Request Body (JSON):
        { "doctor_id": 1, "status": "Open" }
    
    Valid statuses: "Open", "Break", "Closed"
    
    Rules:
    - Cannot close if patients are waiting
    - Can toggle between Open/Break/Closed
    """
    data = request.get_json()
    
    if not data or 'doctor_id' not in data or 'status' not in data:
        return jsonify({'error': 'doctor_id and status are required'}), 400
    
    new_status = data['status']
    if new_status not in ['Open', 'Break', 'Closed']:
        return jsonify({'error': 'Invalid status. Must be Open, Break, or Closed'}), 400
    
    doctor = Doctor.query.get(data['doctor_id'])
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404
    
    # Cannot close if patients are waiting
    if new_status == 'Closed':
        waiting = doctor.get_waiting_count()
        if waiting > 0:
            return jsonify({
                'error': 'Cannot close clinic',
                'message': f'{waiting} patients are still waiting. Please serve or cancel all patients first.'
            }), 400
    
    try:
        doctor.status = new_status
        db.session.commit()
        
        return jsonify({
            'message': f'Status updated to {new_status}',
            'status': doctor.get_effective_status(),
            'doctor_id': doctor.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@doctor_bp.route('/doctor/reset_queue', methods=['POST'])
def reset_queue():
    """
    Reset the queue for a doctor.
    
    Request Body (JSON):
        { "doctor_id": 1 }
    
    Rules:
    - Only allowed when waiting count is 0
    - Resets current_token_number to 0
    """
    data = request.get_json()
    
    if not data or 'doctor_id' not in data:
        return jsonify({'error': 'doctor_id is required'}), 400
    
    doctor = Doctor.query.get(data['doctor_id'])
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404
    
    waiting = doctor.get_waiting_count()
    if waiting > 0:
        return jsonify({
            'error': 'Cannot reset queue',
            'message': f'{waiting} patients are still waiting'
        }), 400
    
    try:
        doctor.current_token_number = 0
        db.session.commit()
        
        return jsonify({
            'message': 'Queue reset successfully',
            'current_token_number': 0,
            'waiting_count': 0
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@doctor_bp.route('/doctor/delete', methods=['POST'])
def delete_doctor():
    """
    Delete a doctor and their clinic from the system.
    
    Request Body (JSON):
        { "doctor_id": 1 }
    
    Logic:
    - Cancels all waiting tokens for this doctor
    - Deletes the doctor record
    - If no other doctors belong to the same clinic, deletes the clinic too
    - Clears localStorage on the frontend side
    """
    data = request.get_json()
    
    if not data or 'doctor_id' not in data:
        return jsonify({'error': 'doctor_id is required'}), 400
    
    doctor = Doctor.query.get(data['doctor_id'])
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404
    
    try:
        clinic_id = doctor.clinic_id
        
        # Cancel all waiting tokens for this doctor
        Token.query.filter_by(
            doctor_id=doctor.id,
            status='waiting'
        ).update({'status': 'cancelled'})
        
        # Delete the doctor
        db.session.delete(doctor)
        db.session.flush()
        
        # Check if the clinic has any other doctors
        other_doctors = Doctor.query.filter_by(clinic_id=clinic_id).count()
        if other_doctors == 0:
            clinic = Clinic.query.get(clinic_id)
            if clinic:
                db.session.delete(clinic)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Doctor and clinic deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500


# ============ EXISTING ENDPOINTS (kept for backward compatibility) ============


@doctor_bp.route('/current_token/<int:doctor_id>', methods=['GET'])
def get_current_token(doctor_id):
    """
    Get the currently active (serving) token for a doctor.
    Used by patient queue_status page.
    """
    doctor = Doctor.query.get(doctor_id)
    
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404
    
    waiting_count = doctor.get_waiting_count()
    avg_time = doctor.get_average_consultation_time()
    
    response = {
        'doctor_id': doctor.id,
        'doctor_name': doctor.name,
        'current_token_number': doctor.current_token_number,
        'waiting_count': waiting_count,
        'status': doctor.get_effective_status(),
        'average_consultation_time': avg_time
    }
    
    return jsonify(response), 200


@doctor_bp.route('/doctor_queue/<int:doctor_id>', methods=['GET'])
def get_doctor_queue(doctor_id):
    """
    Get all waiting tokens for a doctor (full queue view).
    """
    doctor = Doctor.query.get(doctor_id)
    
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404
    
    waiting_tokens = doctor.get_waiting_tokens()
    
    return jsonify({
        'doctor_id': doctor.id,
        'doctor_name': doctor.name,
        'waiting_tokens': [{'token_number': t.token_number} for t in waiting_tokens],
        'total_waiting': len(waiting_tokens)
    }), 200
