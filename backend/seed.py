"""
CareQueue — Database Seed Script
Wipes all data and inserts 3 clean demo doctors for portfolio/LinkedIn showcase.
Run: python seed.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from database import db
from models import Clinic, Doctor, Patient, Token
import uuid

app = create_app('development')

with app.app_context():

    # ── 1. WIPE ──────────────────────────────────────────────────────────────
    print("[*] Clearing all existing data...")
    Token.query.delete()
    Patient.query.delete()
    Doctor.query.delete()
    Clinic.query.delete()
    db.session.commit()
    print("[OK] Database cleared.\n")

    # ── 2. SEED ──────────────────────────────────────────────────────────────

    # --- Clinic 1 ---
    c1 = Clinic(name="Arogya Wellness Clinic", location="Satellite Road, Ahmedabad")
    db.session.add(c1)
    db.session.flush()   # get c1.id

    d1 = Doctor(
        name="Dr. Arjun Mehta",
        specialization="Homeopathy Doctor",
        licence_number="GJ1001",
        clinic_id=c1.id,
        opd_start_time="09:00",
        opd_end_time="13:00",
        status="Open",
        current_token_number=0,
        api_key=str(uuid.uuid4())
    )
    d1.set_password("1234")
    db.session.add(d1)

    # --- Clinic 2 ---
    c2 = Clinic(name="CurePlus Child Care", location="Navrangpura, Ahmedabad")
    db.session.add(c2)
    db.session.flush()

    d2 = Doctor(
        name="Dr. Priya Sharma",
        specialization="Pediatrician",
        licence_number="GJ1002",
        clinic_id=c2.id,
        opd_start_time="10:00",
        opd_end_time="14:00",
        status="Open",
        current_token_number=0,
        api_key=str(uuid.uuid4())
    )
    d2.set_password("1234")
    db.session.add(d2)

    # --- Clinic 3 ---
    c3 = Clinic(name="HeartBeat Cardiac Centre", location="SG Highway, Ahmedabad")
    db.session.add(c3)
    db.session.flush()

    d3 = Doctor(
        name="Dr. Rahul Verma",
        specialization="Cardiologist",
        licence_number="GJ1003",
        clinic_id=c3.id,
        opd_start_time="14:00",
        opd_end_time="18:00",
        status="Closed",
        current_token_number=0,
        api_key=str(uuid.uuid4())
    )
    d3.set_password("1234")
    db.session.add(d3)

    db.session.commit()

    # ── 3. PATIENTS + TOKENS ─────────────────────────────────────────────────

    from models import Patient, Token
    from datetime import datetime

    patients_data = [
        # Clinic 1 — Arogya Wellness (Dr. Arjun Mehta)
        ("Ravi Kumar",    "9876501001", d1),
        ("Sneha Patel",   "9876501002", d1),
        ("Amit Joshi",    "9876501003", d1),
        ("Meera Desai",   "9876501004", d1),
        # Clinic 2 — CurePlus Child Care (Dr. Priya Sharma)
        ("Kiran Shah",    "9876502001", d2),
        ("Pooja Mehta",   "9876502002", d2),
        ("Rohan Gupta",   "9876502003", d2),
        # Clinic 3 (Closed) — no patients added
    ]

    token_num = {}   # track per-doctor token numbers

    for name, phone, doctor in patients_data:
        # Create patient
        p = Patient(name=name, phone_number=phone)
        p.set_password("1234")
        db.session.add(p)
        db.session.flush()

        # Assign next token
        did = doctor.id
        token_num[did] = token_num.get(did, 0) + 1

        t = Token(
            patient_id=p.id,
            doctor_id=did,
            token_number=token_num[did],
            status='waiting',
            created_at=datetime.now()
        )
        db.session.add(t)

    db.session.commit()

    # ── 4. SUMMARY ───────────────────────────────────────────────────────────
    print("[OK] Seeded 3 demo doctors:\n")
    print("+---------------------------+-------------------+------+---------+")
    print("|  Clinic                   | Doctor            | PIN  | Status  |")
    print("+---------------------------+-------------------+------+---------+")
    print("|  Arogya Wellness Clinic   | Dr. Arjun Mehta   | 1234 | Open    |")
    print("|  CurePlus Child Care      | Dr. Priya Sharma  | 1234 | Open    |")
    print("|  HeartBeat Cardiac Centre | Dr. Rahul Verma   | 1234 | Closed  |")
    print("+---------------------------+-------------------+------+---------+")
    print("\nLicence Numbers:  GJ1001 / GJ1002 / GJ1003")
    print("PIN for all:      1234")
    print("\nWebsite: http://localhost:5000")

