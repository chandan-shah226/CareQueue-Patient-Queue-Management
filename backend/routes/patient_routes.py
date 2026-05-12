"""
Patient-related API endpoints for CareQueue.

Endpoints:
- POST /api/register_patient  - Register a new patient (requires name, phone, 4-digit PIN)
- POST /api/login_patient     - Authenticate existing patient (phone + PIN)
- GET  /api/queue_status/<doctor_id> - Get queue status with estimated wait

Security:
- Passwords (4-digit PINs) are hashed with bcrypt (12 rounds). Never stored in plain text.
- Rate limiter (5 attempts / minute per IP) protects against brute-force PIN attacks.
- password_hash is NEVER returned in any API response.
"""

from flask import Blueprint, request, jsonify
from database import db
from models import Patient, Doctor, Token
from datetime import datetime
import re

# ── Blueprint ──────────────────────────────────────────────────────────────────
patient_bp = Blueprint('patient', __name__, url_prefix='/api')

# ── Rate-limit store (in-memory dictionary) ────────────────────────────────────
# Format: { ip_address: [timestamp, timestamp, ...] }
# Simple sliding-window: max MAX_ATTEMPTS within WINDOW_SECONDS
import time
from collections import defaultdict

_login_attempts: dict = defaultdict(list)
MAX_ATTEMPTS = 5         # max failed login tries
WINDOW_SECONDS = 60      # per minute


def _is_rate_limited(ip: str) -> bool:
    """Return True if the IP has exceeded MAX_ATTEMPTS in the last WINDOW_SECONDS."""
    now = time.time()
    # Prune old timestamps outside the window
    _login_attempts[ip] = [t for t in _login_attempts[ip] if now - t < WINDOW_SECONDS]
    return len(_login_attempts[ip]) >= MAX_ATTEMPTS


def _record_failed_attempt(ip: str) -> None:
    """Record a failed login attempt timestamp for rate-limiting."""
    _login_attempts[ip].append(time.time())


def _validate_pin(pin: str) -> tuple[bool, str]:
    """
    Validate that pin is exactly 4 numeric digits.
    
    Returns:
        (True, '') if valid
        (False, reason) if invalid
    """
    if not pin:
        return False, "PIN is required"
    if not re.fullmatch(r'\d{4}', pin):
        return False, "PIN must be exactly 4 digits (numbers only)"
    return True, ''


# ── Routes ─────────────────────────────────────────────────────────────────────

@patient_bp.route('/register_patient', methods=['POST'])
def register_patient():
    """
    Register a NEW patient with a name, phone number, and 4-digit PIN.

    Request Body (JSON):
        {
            "phone_number": "9876543210",   // 10-digit string
            "name": "John Doe",
            "pin": "1234"                   // exactly 4 numeric digits
        }

    Responses:
        201 - Patient registered successfully
        400 - Validation error (missing fields / bad format)
        409 - Patient already exists (use /login_patient instead)
    """
    data = request.get_json(silent=True)

    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    phone_number = data.get('phone_number', '').strip()
    name = data.get('name', '').strip()
    pin = str(data.get('pin', '')).strip()

    # ── Field presence ──────────────────────────────────────────────────────
    missing = []
    if not phone_number:
        missing.append('phone_number')
    if not name:
        missing.append('name')
    if not pin:
        missing.append('pin')
    if missing:
        return jsonify({
            'error': 'Missing required fields',
            'missing': missing
        }), 400

    # ── Phone validation ────────────────────────────────────────────────────
    if not re.fullmatch(r'\d{10}', phone_number):
        return jsonify({
            'error': 'Invalid phone number',
            'message': 'Phone number must be exactly 10 digits'
        }), 400

    # ── PIN validation ──────────────────────────────────────────────────────
    pin_ok, pin_msg = _validate_pin(pin)
    if not pin_ok:
        return jsonify({
            'error': 'Invalid PIN format',
            'message': pin_msg
        }), 400

    # ── Duplicate check ─────────────────────────────────────────────────────
    existing = Patient.query.filter_by(phone_number=phone_number).first()
    if existing:
        return jsonify({
            'error': 'Patient already exists',
            'message': 'An account with this phone number already exists. Please log in.',
            'is_existing': True
        }), 409

    # ── Create patient ──────────────────────────────────────────────────────
    new_patient = Patient(name=name, phone_number=phone_number)
    new_patient.set_password(pin)          # bcrypt hash — NEVER plain text

    db.session.add(new_patient)
    db.session.commit()

    return jsonify({
        'message': 'Patient registered successfully',
        'patient': new_patient.to_dict()   # password_hash excluded by to_dict()
    }), 201


@patient_bp.route('/login_patient', methods=['POST'])
def login_patient():
    """
    Authenticate an EXISTING patient using phone number + 4-digit PIN.

    Request Body (JSON):
        {
            "phone_number": "9876543210",
            "pin": "1234"
        }

    Responses:
        200 - Login successful
        400 - Missing / invalid fields
        401 - Incorrect PIN
        404 - Patient not found
        429 - Too many attempts (rate limited)
    """
    ip = request.remote_addr or '127.0.0.1'

    # ── Rate limiting ───────────────────────────────────────────────────────
    if _is_rate_limited(ip):
        return jsonify({
            'error': 'Too many attempts',
            'message': 'Too many failed login attempts. Please wait 1 minute and try again.'
        }), 429

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    phone_number = data.get('phone_number', '').strip()
    pin = str(data.get('pin', '')).strip()

    # ── Field presence ──────────────────────────────────────────────────────
    if not phone_number or not pin:
        return jsonify({
            'error': 'Missing required fields',
            'message': 'Both phone_number and pin are required'
        }), 400

    # ── Phone validation ────────────────────────────────────────────────────
    if not re.fullmatch(r'\d{10}', phone_number):
        return jsonify({
            'error': 'Invalid phone number format',
            'message': 'Phone number must be exactly 10 digits'
        }), 400

    # ── PIN format validation ────────────────────────────────────────────────
    pin_ok, pin_msg = _validate_pin(pin)
    if not pin_ok:
        return jsonify({
            'error': 'Invalid PIN format',
            'message': pin_msg
        }), 400

    # ── Patient lookup ───────────────────────────────────────────────────────
    patient = Patient.query.filter_by(phone_number=phone_number).first()
    if not patient:
        _record_failed_attempt(ip)
        return jsonify({
            'error': 'User not found',
            'message': 'No account found with this phone number. Please register first.'
        }), 404

    # ── Password check ───────────────────────────────────────────────────────
    if not patient.check_password(pin):
        _record_failed_attempt(ip)
        return jsonify({
            'error': 'Incorrect PIN',
            'message': 'The PIN you entered is incorrect. Please try again.'
        }), 401

    # ── Success ──────────────────────────────────────────────────────────────
    # Clear failed-attempt history on successful login
    _login_attempts.pop(ip, None)

    return jsonify({
        'message': 'Login successful',
        'patient': patient.to_dict()       # password_hash excluded by to_dict()
    }), 200


@patient_bp.route('/check_patient', methods=['POST'])
def check_patient():
    """
    Check if a phone number belongs to a registered patient.
    Used by frontend to decide between "Register" and "Login" flows.

    Request Body (JSON):
        { "phone_number": "9876543210" }

    Responses:
        200 - { "exists": true/false, "has_password": true/false }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    phone_number = data.get('phone_number', '').strip()

    if not re.fullmatch(r'\d{10}', phone_number):
        return jsonify({
            'error': 'Invalid phone number',
            'message': 'Phone number must be exactly 10 digits'
        }), 400

    patient = Patient.query.filter_by(phone_number=phone_number).first()
    if not patient:
        return jsonify({'exists': False, 'has_password': False}), 200

    return jsonify({
        'exists': True,
        'has_password': patient.has_password(),
        'name': patient.name      # show a greeting on the login step
    }), 200


@patient_bp.route('/set_patient_pin', methods=['POST'])
def set_patient_pin():
    """
    Set a 4-digit PIN for an EXISTING patient who does not yet have one.

    This covers two scenarios:
      1. Legacy accounts created before the password feature was added.
      2. New patients who somehow skipped PIN creation (shouldn't happen, but safe).

    The request is accepted ONLY if the patient exists AND has no PIN set.
    No additional secret is required — the phone number itself is the proof of
    identity at this stage (the patient is in the middle of an active session).

    Request Body (JSON):
        {
            "phone_number": "9876543210",
            "pin": "1234"               // exactly 4 numeric digits
        }

    Responses:
        200 - PIN set successfully, patient object returned (auto-login)
        400 - Validation error
        404 - Patient not found
        409 - Patient already has a PIN (use /login_patient instead)
        429 - Rate limited
    """
    ip = request.remote_addr or '127.0.0.1'

    # Rate-limit this endpoint too (same store as login)
    if _is_rate_limited(ip):
        return jsonify({
            'error': 'Too many attempts',
            'message': 'Too many requests. Please wait 1 minute and try again.'
        }), 429

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    phone_number = data.get('phone_number', '').strip()
    pin = str(data.get('pin', '')).strip()

    # ── Validate phone ──────────────────────────────────────────────────────
    if not re.fullmatch(r'\d{10}', phone_number):
        return jsonify({
            'error': 'Invalid phone number',
            'message': 'Phone number must be exactly 10 digits'
        }), 400

    # ── Validate PIN format ─────────────────────────────────────────────────
    pin_ok, pin_msg = _validate_pin(pin)
    if not pin_ok:
        return jsonify({
            'error': 'Invalid PIN format',
            'message': pin_msg
        }), 400

    # ── Patient lookup ──────────────────────────────────────────────────────
    patient = Patient.query.filter_by(phone_number=phone_number).first()
    if not patient:
        _record_failed_attempt(ip)
        return jsonify({
            'error': 'User not found',
            'message': 'No account found with this phone number. Please register first.'
        }), 404

    # ── Guard: already has a PIN ────────────────────────────────────────────
    if patient.has_password():
        return jsonify({
            'error': 'PIN already set',
            'message': 'This account already has a PIN. Please log in normally.',
            'redirect': 'login'
        }), 409

    # ── Set the PIN ─────────────────────────────────────────────────────────
    patient.set_password(pin)
    db.session.commit()

    # Clear any failed-attempt counters for this IP
    _login_attempts.pop(ip, None)

    return jsonify({
        'message': 'PIN set successfully',
        'patient': patient.to_dict()   # password_hash excluded by to_dict()
    }), 200


@patient_bp.route('/generate_token', methods=['POST'])
def generate_token():
    """
    Generate a queue token for a patient to see a doctor.
    """
    data = request.get_json(silent=True)

    if not data or 'patient_id' not in data or 'doctor_id' not in data:
        return jsonify({
            'error': 'Missing required fields',
            'required': ['patient_id', 'doctor_id']
        }), 400

    patient_id = data['patient_id']
    doctor_id = data['doctor_id']

    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404

    if doctor.get_effective_status() != "Open":
        return jsonify({
            'error': 'Clinic not open',
            'message': 'This doctor is not currently accepting patients'
        }), 400

    token_number = doctor.get_next_token_number()

    new_token = Token(
        patient_id=patient_id,
        doctor_id=doctor_id,
        token_number=token_number,
        status='waiting',
        created_at=datetime.now()
    )

    db.session.add(new_token)
    db.session.commit()

    return jsonify({
        'message': 'Token generated successfully',
        'token': new_token.to_dict(),
        'queue_position': doctor.get_waiting_count()
    }), 201


@patient_bp.route('/queue_status/<int:doctor_id>', methods=['GET'])
def get_queue_status(doctor_id):
    """
    Get queue status for a doctor including estimated wait time.
    Used by patient queue_status page.
    """
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404

    waiting_count = doctor.get_waiting_count()
    avg_time = doctor.get_average_consultation_time()

    return jsonify({
        'doctor_id': doctor_id,
        'doctor_name': doctor.name,
        'current_token_number': doctor.current_token_number,
        'waiting_count': waiting_count,
        'status': doctor.get_effective_status(),
        'average_consultation_time': avg_time
    }), 200
