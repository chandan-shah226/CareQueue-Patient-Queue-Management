"""
Database initialization and utilities for CareQueue.

This module provides the SQLAlchemy instance and helper functions
for database operations.
"""

from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
# This will be initialized with the Flask app in app.py
db = SQLAlchemy()


def init_db(app):
    """
    Initialize the database with the Flask application.
    
    Args:
        app: Flask application instance
        
    This function:
    1. Binds the database to the Flask app
    2. Creates all tables if they don't exist
    """
    db.init_app(app)
    
    with app.app_context():
        # Import models here to avoid circular imports
        from models import Clinic, Doctor, Patient, Token
        
        # Create all tables
        db.create_all()
        print("[OK] Database tables created successfully")


def drop_all_tables(app):
    """
    Drop all database tables. Use with caution!
    
    Args:
        app: Flask application instance
        
    This is useful for development/testing when you need to reset the database.
    """
    with app.app_context():
        db.drop_all()
        print(" All tables dropped")
