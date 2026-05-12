"""
Configuration settings for CareQueue Flask application.

This module contains configuration classes for different environments.
The database is configured to use SQLite with settings that make future
PostgreSQL migration straightforward.
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class with common settings."""
    
    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    # Using SQLite with absolute path for development
    # For PostgreSQL migration, change to: postgresql://user:password@localhost/carequeue
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    _db_path = os.path.join(BASE_DIR, '..', 'carequeue.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + _db_path.replace('\\', '/')
    
    # Disable modification tracking to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Enable query echo for debugging (set to False in production)
    SQLALCHEMY_ECHO = False
    
    # CORS settings - allow all origins in development
    # In production, restrict to specific domains
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    
    # JSON configuration
    JSON_SORT_KEYS = False  # Preserve key order in JSON responses


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_ECHO = False  # Disable query echo in production


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # In-memory database for tests


# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
