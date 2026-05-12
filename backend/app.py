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


if __name__ == '__main__':
    # Create the app
    app = create_app('development')
    
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
