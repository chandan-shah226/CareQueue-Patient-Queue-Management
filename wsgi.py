"""
WSGI entry point for production deployment (Render / Gunicorn).
Gunicorn uses this file: gunicorn wsgi:app
"""
import sys
import os

# Make sure backend/ is in the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app, auto_seed, start_keep_alive

app = create_app('production')

# Seed demo data if database is empty (runs on every cold start)
auto_seed(app)

# Keep-alive ping thread to prevent Render free tier from sleeping
start_keep_alive(app)

if __name__ == '__main__':
    app.run()
