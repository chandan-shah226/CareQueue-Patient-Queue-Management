"""
CareQueue Flask Application - Main Entry Point

This is the main Flask application file that:
1. Initializes Flask with CORS enabled
2. Configures the database
3. Registers all API route blueprints
4. Serves static files and templates
5. Provides the development server

Run with: python app.py
The app will start on   
"""

from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
import os
import threading
import time
import uuid
import requests


# Import configuration
from config import config

# Import database initialization
from database import db, init_db

# Import route blueprints
from routes.patient_routes import patient_bp
from routes.doctor_routes import doctor_bp
from routes.clinic_routes import clinic_bp


def create_app(config_name='development'):
    """
    Application factory pattern for creating Flask app.
    
    Args:
        config_name: Configuration to use ('development', 'production', 'testing')
        
    Returns:
        Configured Flask application instance
    """
    # Initialize Flask app
    app = Flask(
        __name__,
        static_folder='../static',  # Static files (CSS, JS)
        template_folder='../templates'  # HTML templates
    )
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Enable CORS for all routes
    # This allows the frontend to make API calls from different origins
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",  # In production, restrict to specific domains
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "x-api-key"]
        }
    })
    
    # Initialize database
    init_db(app)
    
    # Register blueprints (API routes)
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(clinic_bp)
    
    # Route: Serve role_select.html as the landing page
    @app.route('/')
    def index():
        """Serve the role selection landing page."""
        return render_template('role_select.html')

    # Route: Serve index.html as the patient login page
    @app.route('/patient_login')
    def patient_login():
        """Serve the patient login page."""
        return render_template('index.html')

    # Route: Serve doctor_login page
    @app.route('/doctor_login')
    def doctor_login():
        """Serve the doctor login page."""
        return render_template('doctor_login.html')
    
    # Route: Serve doctor_register page
    @app.route('/doctor_register')
    def doctor_register():
        """Serve the doctor registration page."""
        return render_template('doctor_register.html')
    
    # Route: Serve doctor_dashboard page
    @app.route('/doctor_dashboard')
    def doctor_dashboard():
        """Serve the doctor dashboard page."""
        return render_template('doctor_dashboard.html')
    
    # Route: Serve select_clinic.html
    @app.route('/select_clinic')
    def select_clinic():
        """Serve the clinic selection page."""
        return render_template('select_clinic.html')
    
    # Route: Serve clinic_details.html
    @app.route('/clinic_details')
    def clinic_details():
        """Serve the clinic details page."""
        return render_template('clinic_details.html')
    
    # Route: Health check endpoint
    @app.route('/health')
    def health():
        """Simple health check endpoint."""
        return {'status': 'healthy', 'message': 'CareQueue API is running'}, 200
    
    # Route: Serve queue_status.html
    @app.route('/queue_status')
    def queue_status():
        """Serve the queue status page."""
        return render_template('queue_status.html')
    
    return app


def auto_seed(app):
    """
    Seed the database with demo data if it is empty.
    Runs once at startup — safe to call multiple times.
    """
    from models import Clinic, Doctor, Patient, Token
    from datetime import datetime

    with app.app_context():
        from database import db
        if Clinic.query.count() > 0:
            print("[seed] Data already exists — skipping auto-seed.")
            return

        print("[seed] Empty database detected — seeding demo data...")

        # Clinic 1
        c1 = Clinic(name="Arogya Wellness Clinic", location="Satellite Road, Ahmedabad")
        db.session.add(c1); db.session.flush()
        d1 = Doctor(name="Dr. Arjun Mehta", specialization="Homeopathy Doctor",
                    licence_number="GJ1001", clinic_id=c1.id,
                    opd_start_time="09:00", opd_end_time="13:00",
                    status="Open", current_token_number=0, api_key=str(uuid.uuid4()))
        d1.set_password("1234"); db.session.add(d1)

        # Clinic 2
        c2 = Clinic(name="CurePlus Child Care", location="Navrangpura, Ahmedabad")
        db.session.add(c2); db.session.flush()
        d2 = Doctor(name="Dr. Priya Sharma", specialization="Pediatrician",
                    licence_number="GJ1002", clinic_id=c2.id,
                    opd_start_time="10:00", opd_end_time="14:00",
                    status="Open", current_token_number=0, api_key=str(uuid.uuid4()))
        d2.set_password("1234"); db.session.add(d2)

        # Clinic 3
        c3 = Clinic(name="HeartBeat Cardiac Centre", location="SG Highway, Ahmedabad")
        db.session.add(c3); db.session.flush()
        d3 = Doctor(name="Dr. Rahul Verma", specialization="Cardiologist",
                    licence_number="GJ1003", clinic_id=c3.id,
                    opd_start_time="14:00", opd_end_time="18:00",
                    status="Closed", current_token_number=0, api_key=str(uuid.uuid4()))
        d3.set_password("1234"); db.session.add(d3)
        db.session.flush()

        # Patients + tokens for open clinics only
        patients = [
            ("Ravi Kumar",  "9876501001", d1),
            ("Sneha Patel", "9876501002", d1),
            ("Amit Joshi",  "9876501003", d1),
            ("Meera Desai", "9876501004", d1),
            ("Kiran Shah",  "9876502001", d2),
            ("Pooja Mehta", "9876502002", d2),
            ("Rohan Gupta", "9876502003", d2),
        ]
        token_num = {}
        for name, phone, doc in patients:
            p = Patient(name=name, phone_number=phone)
            p.set_password("1234"); db.session.add(p); db.session.flush()
            token_num[doc.id] = token_num.get(doc.id, 0) + 1
            db.session.add(Token(patient_id=p.id, doctor_id=doc.id,
                                 token_number=token_num[doc.id],
                                 status='waiting', created_at=datetime.now()))

        db.session.commit()
        print("[seed] Demo data seeded successfully.")


def start_keep_alive(app):
    """
    Background thread that pings the /health endpoint every 14 minutes
    so Render free tier never spins down the service.
    """
    def ping():
        # Wait for server to fully start
        time.sleep(30)
        base_url = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:5000')
        url = f"{base_url}/health"
        while True:
            try:
                r = requests.get(url, timeout=10)
                print(f"[keep-alive] Pinged {url} — {r.status_code}")
            except Exception as e:
                print(f"[keep-alive] Ping failed: {e}")
            time.sleep(14 * 60)   # every 14 minutes

    t = threading.Thread(target=ping, daemon=True)
    t.start()


if __name__ == '__main__':
    # Create the app
    config_name = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config_name)

    # Auto-seed demo data if database is empty
    auto_seed(app)

    # Keep-alive ping (prevents Render free tier from sleeping)
    start_keep_alive(app)

    
    print("\n" + "="*60)
    print("🏥 CareQueue Backend Server Starting...")
    print("="*60)
    print(f"📍 Server: http://localhost:5000")
    print(f"📍 API Base: http://localhost:5000/api")
    print(f"📍 Health Check: http://localhost:5000/health")
    print("="*60)
    print("\n💡 API Endpoints:")
    print("   POST   /api/register_patient")
    print("   POST   /api/generate_token")
    print("   GET    /api/current_token/<doctor_id>")
    print("   POST   /api/doctor/login")
    print("   POST   /api/doctor/register")
    print("   POST   /api/doctor/mark_done")
    print("   POST   /api/doctor/update_status")
    print("   POST   /api/doctor/reset_queue")
    print("   GET    /api/doctor/dashboard/<doctor_id>")
    print("   GET    /api/doctor_queue/<doctor_id>")
    print("   GET    /api/clinics")
    print("   GET    /api/clinic/<clinic_id>")
    print("="*60 + "\n")
    
    # Run the development server
    # debug=True enables auto-reload and detailed error pages
    app.run(
        host='0.0.0.0',  # Listen on all network interfaces
        port=5000,
        debug=True
    )
