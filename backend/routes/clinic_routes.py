"""
Clinic-related API endpoints for CareQueue.

Endpoints:
- GET /api/clinics - List all clinics with statistics
- GET /api/clinic/<clinic_id> - Get specific clinic details
"""

from flask import Blueprint, jsonify
from models import Clinic, Doctor

# Create blueprint
clinic_bp = Blueprint('clinic', __name__, url_prefix='/api')


@clinic_bp.route('/clinics', methods=['GET'])
def get_all_clinics():
    """
    Get all clinics with their doctors and queue statistics.
    
    Returns clinic name, location, doctor name, OPD timings,
    status (Open/Break/Closed), current_token, and waiting_count.
    
    Only includes doctors who have a licence_number (dynamically registered).
    """
    clinics = Clinic.query.all()
    
    clinics_data = []
    for clinic in clinics:
        clinic_dict = clinic.to_dict()
        
        # Add doctors with statistics
        clinic_dict['doctors'] = []
        for doctor in clinic.doctors:
            doctor_data = doctor.to_dict(include_stats=True)
            clinic_dict['doctors'].append(doctor_data)
        
        # Only include clinics that have at least one doctor
        if clinic_dict['doctors']:
            clinics_data.append(clinic_dict)
    
    return jsonify({
        'clinics': clinics_data,
        'total_clinics': len(clinics_data)
    }), 200


@clinic_bp.route('/clinic/<int:clinic_id>', methods=['GET'])
def get_clinic_details(clinic_id):
    """
    Get detailed information about a specific clinic.
    """
    clinic = Clinic.query.get(clinic_id)
    
    if not clinic:
        return jsonify({'error': 'Clinic not found'}), 404
    
    clinic_dict = clinic.to_dict()
    
    # Add doctors with statistics
    clinic_dict['doctors'] = [
        doctor.to_dict(include_stats=True) 
        for doctor in clinic.doctors
    ]
    
    return jsonify(clinic_dict), 200
