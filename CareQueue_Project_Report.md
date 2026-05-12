# PROJECT REPORT
# CareQueue – Smart Patient Queue Management System

## ABSTRACT
Adaptation of digital queue management increases operational efficiency in clinics and drastically improves the overall patient experience. It reduces physical crowding in waiting rooms and unpredictable waiting times to a minimum. The product aims to solve the issues around traditional manual outpatient department (OPD) queues by leveraging a centralized web-based architecture. It aims to deliver an automated solution which has the ability to allow patients to generate virtual tokens remotely via a Web Application, and provides an interface for doctors to manage patient flow. It also dynamically provides insights to patients regarding their estimated wait times and the live status of the queue. This solution is completely hardware-independent and lightweight, meaning clinics do not need to worry about provisioning specific physical kiosks or planning for expensive dedicated servers. It aims to provide an accessible platform where clinics and patients can utilize and take advantage of streamlined queue operations.
 
The project features a Token Generation pipeline, a real-time polling platform to broadcast queue data, Wait-Time Calculation algorithms, and Authenticated access for Doctor Dashboards. The procedural workflow of live clinic environments (e.g., Vital Wave Rehabs) was evaluated to deduce standard consultation constraints, and safe relational database schemas were integrated using SQLite to ensure data integrity, track accurate operational timeframes, and decide appropriate queue pacing.

---

## 1. TABLE OF CONTENTS

1. [Introduction / Objectives](#2-introduction--objectives)
2. [System Analysis](#3-system-analysis)
    - a. Identification of Need
    - b. Preliminary Investigation
    - c. Feasibility Study
    - d. Project Planning
    - e. Project Scheduling
    - f. Software Requirement Specification (SRS)
    - g. Software Engineering Paradigm
    - h. Data Models and Diagrams
3. [System Design](#4-system-design)
    - a. Modularization
    - b. Data Integrity & Constraints
    - c. Database Design
    - d. User Interface Design
    - e. Test Case Design
4. [Coding](#5-coding)
    - a. SQL Commands
    - b. Complete Project Coding
    - c. Code Description
5. [Standardization of Coding](#6-standardization-of-coding)
6. [Testing](#7-testing)
7. [System Security Measures](#8-system-security-measures)
8. [Cost Estimation](#9-cost-estimation)
9. [Reports](#10-reports)
10. [Future Scope](#11-future-scope)
11. [Bibliography](#12-bibliography)
12. [Appendices](#13-appendices)
13. [Glossary](#14-glossary)

---

## 2. INTRODUCTION / OBJECTIVES

### Introduction
The healthcare industry frequently struggles with managing patient flow, leading to overcrowded waiting rooms, increased cross-infection risks, and patient dissatisfaction. "CareQueue – Smart Patient Queue Management System" is developed to eliminate these bottlenecks by digitalizing the traditional outpatient department (OPD) queues. CareQueue is a web-based application built using Python (Flask), SQLite, HTML, CSS, and vanilla JavaScript. It allows patients to log in using their 10-digit mobile number, securely authenticate, browse available clinics and doctors, and join a real-time virtual queue. Instead of waiting physically at the clinic, patients can track their token number, see the number of patients ahead of them, and view their estimated wait times from anywhere. For doctors, it provides an intuitive dashboard to manage their OPD status, track patient flow, mark consultations as done, and dynamically calculate average consultation times.

### Objectives
*   **Virtual Ticketing:** To allow patients to generate queue tokens digitally from their mobile devices using their phone number without requiring a complex registration process.
*   **Real-time Queue Tracking:** To provide patients with live updates on the current token being served, the number of patients ahead of them, and an algorithmically estimated wait time.
*   **Doctor Dashboard Management:** To equip doctors with a streamlined interface where they can update their clinic status (Open, Break, Closed), mark consultations as resolved, and view real-time statistics of their queue.
*   **Clinic and Doctor Aggregation:** To allow users to view multiple clinics (e.g., Vital Wave Rehabs, Share & Heal, Health Care) and select specific doctors based on OPD timings.
*   **Automated Time Estimation:** To dynamically calculate the average consultation time per doctor based on the time intervals between previous patients being marked as 'served'.
*   **Crowd Reduction:** To actively reduce physical waiting times in clinics, subsequently reducing the chance of communicable disease spread in closed waiting areas.

---

## 3. SYSTEM ANALYSIS

### a. Identification of Need
In a real-world scenario, patients visiting clinics must manually write their names in a register or collect physical tokens. This manual queue system forces patients to sit in the waiting room for unpredictable periods. Because doctors cannot universally predict consultation lengths, patients might wait anywhere from 15 minutes to 3 hours. 

CareQueue is explicitly required to address these issues. By providing a system where patients can see that Token #12 is currently being served while they hold Token #20, and that the average consultation takes 5 minutes, they know they have approximately 40 minutes before they need to be at the clinic. This solves the immediate real-world problem of time wastage and poor patient experience.

### b. Preliminary Investigation
**Existing System:**
The existing system at clinics like "Vital Wave Rehabs" and "Share & Heal" is entirely manual. The receptionist issues a physical numbered ticket to the patient. Patients must continuously ask the receptionist how many people are ahead of them.
**Problems in Existing System:**
*   Patients have zero visibility into the queue progress unless they are physically present.
*   Receptionists are overburdened with inquiries regarding waiting times.
*   Token management is prone to human error (e.g., lost tickets, skipped numbers).
**Proposed System (CareQueue):**
The proposed CareQueue application mitigates these flaws by migrating the list to a centralized SQLite database. Patients join the queue locally via an API (`/api/generate_token`), and the doctor increments the served token via a secure `REST API` endpoint (`/api/doctor/mark_done`). The frontend `queue_status.html` fetches this data continuously, eliminating the need for manual inquiries. 

### c. Feasibility Study
*   **Technical Feasibility:** The system is highly feasible technically. Python 3.10+, Flask 3.0, and SQLite are used. SQLAlchemy handles Object Relational Mapping (ORM), ensuring that database queries are abstracted. The frontend uses standard Web APIs (Fetch API) which are natively supported by all modern browsers.
*   **Economic Feasibility:** The development relies entirely on open-source libraries (Flask, Flask-CORS, SQLAlchemy). The database used is SQLite, eliminating the need for an expensive dedicated database server. Hosting can be done on minimal infrastructure, making it highly economically feasible.
*   **Operational Feasibility:** The usability is intentionally kept simple. Patients only need a 10-digit mobile number to log in (no passwords required). Doctors use a clean dashboard with large buttons (Mark as Done, Pause, Open OPD). It aligns perfectly with user capabilities.
*   **Time Feasibility:** Given the scope, the system was fully developed, integrated, and tested within the allocated academic timeframes, employing rapid prototyping to establish the Flask routes and UI quickly.

### d. Project Planning
The project was divided into 5 standard phases:
1.  **Requirement Phase:** Met with potential users to deduce needed fields (e.g., Doctors need "Break" status, Patients need a "10-digit number" constraint).
2.  **Design Phase:** Wireframed the UI for `index.html`, `select_clinic.html`, and `doctor_dashboard.html`. Structured the 4 main SQL tables (`Clinic`, `Doctor`, `Patient`, `Token`).
3.  **Development Phase:** Built the Flask API backend followed by the Vanilla CSS/JS frontend. Integrated them using CORS and Fetch API.
4.  **Testing Phase:** Tested token increment logic, auto-refresh polling, and estimated wait calculations.
5.  **Deployment Phase:** Finalized `app.py` for local production usage with Flask's built-in application server.

### e. Project Scheduling
**PERT Chart Explanation**
The PERT chart for CareQueue involved parallel tasks. While the SQLite `models.py` representations were being written, the HTML templates (`queue_status.html` and `doctor_dashboard.html`) were partially drafted. The critical path included: `Database Design` -> `Backend API routes (patient_routes.py, doctor_routes.py)` -> `Frontend API Integration` -> `Testing wait-time calculation logic`.

**Gantt Chart (Timeline Table Model):**
| Project Phase | Tasks Assigned | Duration |
| :--- | :--- | :--- |
| Requirement | System analysis, defining constraints | Week 1 |
| DB Design | Creating `models.py` (Clinic, Doctor, Patient, Token) | Week 2 |
| API Backend | `flask`, `patient_routes.py`, `doctor_routes.py` | Week 3-4 |
| UI/Frontend | HTML, CSS grids, `queue_status` UI | Week 5-6 |
| Integration | Fetching REST APIs via JavaScript, CORS | Week 7 |
| Testing | Logic bugs, queue logic, completion popups | Week 8 |

### f. Software Requirement Specification (SRS)
**Functional Requirements:**
*   Patients must be able to log in using only a valid 10-digit mobile number.
*   System must pull a list of distinct active clinics and their doctors.
*   Patients must be able to generate exactly one token per doctor per session.
*   System must display the real-time "Current Token" being served, "Patients Ahead", and dynamically calculated "Estimated Wait".
*   System must auto-refresh patient wait times using an automated JavaScript interval polling mechanism.
*   Doctors must possess a dashboard allowing them to login via a unique `licence_number` (e.g., GJ1334).
*   Doctors must be able to mark patients as "Served", shifting the current Token Number forward and marking the DB row accordingly.
*   Doctors must be able to update OPD status to "Open", "Break", or "Closed".

**Non-functional Requirements:**
*   **Performance:** Backend must serve API requests in < 500ms to allow smooth UI polling every 10 seconds.
*   **Reliability:** The SQLite database must retain queue states even if the local development server is restarted.
*   **Usability:** Mobile-first design is strictly applied via `viewport` meta tags, ensuring `queue_status.html` functions perfectly on smartphones.

### g. Software Engineering Paradigm
**Waterfall Model**
The Waterfall Model was strictly followed for CareQueue's development.
1.  **Requirements:** SRS formulation completed before coding began.
2.  **Design:** The database architecture (`database_architecture.md`) and ER mapping explicitly defined one-to-many relationships before setting up SQLAlchemy.
3.  **Implementation:** Developed `models.py`, followed by `seed_data.py`, then routing modules, and lastly HTML pages.
4.  **Verification:** Validated that Token logic accurately tracked waiting users.
5.  **Maintenance:** Implemented robust try-except error catching in API endpoints to prevent server crash during unforeseen invalid JSON requests.

### h. Data Models and Diagrams

**DFD Level 0 (Context Diagram):**
*   **Patient** -> Enters Mobile Number -> **CareQueue System**
*   **CareQueue System** -> Returns Token Details -> **Patient**
*   **Doctor** -> Sends Status Update (Mark Done) -> **CareQueue System**
*   **CareQueue System** -> Returns Queue Stats -> **Doctor**

**DFD Level 1:**
1. Process 1.0 (Login): Patient provides 10-digit number -> Validated against Database -> Returns Patient ID.
2. Process 2.0 (Select Clinic): Fetch clinic list from DB -> Return to UI.
3. Process 3.0 (Queue Management): Patient joins queue -> Token table updated -> Returns Token ID #. 
4. Process 4.0 (Doctor Interface): Doctor logs in using License Number -> Fetches `Token` table where status = 'waiting' -> Modifies Token to 'served'.

**ER Diagram Description:**
*   **Clinic**: Attributes -> `id` (PK), `name`, `location`. Relationship -> 1 to Many with Doctor.
*   **Doctor**: Attributes -> `id` (PK), `name`, `specialization`, `licence_number`, `clinic_id` (FK), `opd_start_time`, `opd_end_time`, `status`, `current_token_number`. Relationship -> 1 to Many with Token.
*   **Patient**: Attributes -> `id` (PK), `name`, `phone_number`. Relationship -> 1 to Many with Token.
*   **Token**: Attributes -> `id` (PK), `patient_id` (FK), `doctor_id` (FK), `token_number`, `status`, `created_at`, `served_at`.

**Use Case Diagram:**
*   **Actor: Patient**: Use cases include -> Login, View Clinics, Select Doctor, Join Queue, View Queue Status.
*   **Actor: Doctor**: Use cases include -> Login, View Dashboard, Open/Close OPD, Mark Token Done, Reset Queue.

**Sequence Diagram (Joining Queue):**
1. Patient interacts with `select_clinic.html`.
2. UI calls `POST /api/generate_token`.
3. Flask Backend validates constraints (is Clinic Open?).
4. Backend finds MAX token number for the doctor, increments by 1.
5. Backend writes new `Token` to DB.
6. Backend returns JSON response with queue position to UI.
7. UI navigates to `queue_status.html`.

---

## 4. SYSTEM DESIGN

### a. Modularization
The system is divided into well-structured backend modules to ensure scalability:
*   `app.py`: Acts as the main entry point, initializes CORS, loads blueprints.
*   `models.py`: Encapsulates all SQLAlchemy Object definitions.
*   `database.py`: Handles SQLite DB instantiation and context setup.
*   `config.py`: Environment-specific configurations (Base, Dev, Prod).
*   `routes/`:
    *   `patient_routes.py`: Encapsulates API logics for `register_patient`, `generate_token`, and `queue_status`.
    *   `doctor_routes.py`: Deals securely with `doctor/login`, `update_status`, and `mark_done`.
    *   `clinic_routes.py`: Handles fetching overarching clinic configurations and associated doctors.
*   `templates/`: Manages HTML fragments.
*   `static/`: Stores modular CSS code (`doctor_dashboard.css`, `queue_status.css`).

### b. Data Integrity & Constraints
The database specifically uses constraints to guarantee data cleanliness:
*   `licence_number`: Enforced as `UNIQUE` in the Doctor table to prevent duplicate doctor accounts.
*   `phone_number`: Enforced as `UNIQUE` in the Patient table to act as an un-duplicated login signature.
*   **Foreign Key Integrity**: `cascade='all, delete-orphan'` is applied on relationships. If a clinic is deleted, all doctors underneath are deleted. If a doctor is deleted, all corresponding tokens are wiped to ensure no orphaned relational logic exists.
*   `token_number`: Controlled iteratively upon creation. The API computes `max_token + 1` mathematically inside the `get_next_token_number()` method.

### c. Database Design
CareQueue operates up to the 3rd Normal Form (3NF).
*   **Table Clinics:** Stores standard properties.
*   **Table Doctors:** Links back to Clinic via `clinic_id`. Includes specific state variables like `current_token_number` and `status` to avoid calculating from the Token table repeatedly when displaying clinic aggregations.
*   **Table Patients:** Completely independent of Clinics. Focuses purely on patient identification.
*   **Table Tokens:** An associative entity resolving the Many-to-Many mapping of Patients and Doctors. Includes tracking metadata (`created_at`, `served_at`) critical for wait-time predictions.

### d. User Interface Design
CareQueue has a specific, mobile-responsive set of UI flows:
1.  **Login (`index.html`):** Clean, centered interface. The "Login / Continue" button activates dynamically only when exactly 10 digits are typed.
2.  **Clinic Selection (`select_clinic.html`):** Card-based grid populated dynamically. Red styles signify "Closed", Orange for "Break", and Green for "Open".
3.  **Queue Status (`queue_status.html`):** The dashboard of the patient. Uses a prominent centered circle to denote the user's specific token. Contains a blinking "LIVE" dot. Color-coded bullet points dictate "Now Serving" (Blue), "Patients Ahead" (Green), and "Estimated Wait" (Orange). Auto-refreshes every 10 seconds via JS `setInterval`. A completion modal triggers when the user's token is served.
4.  **Doctor Dashboard (`doctor_dashboard.html`):** Professional layout showcasing "Current Token" and "Waiting List". Contains functional grid buttons to easily invoke actions without navigating pages.

### e. Test Case Design
*   **Unit Test 1 (Patient Registration):** Input: `9876543210`. Expected: Server returns Status 200, creates Patient. Input: `abcd`. Expected: Backend rejects, Status 400.
*   **Unit Test 2 (Wait Time Math):** Input: 2 tokens served, difference is 4 mins then 6 mins. Expected: Average time calculates accurately to `5.0`.
*   **System Test 1:** Patient joins queue -> Doctor's dashboard UI Waiting count increments -> Doctor clicks 'Mark Done' -> Patient's UI live-updates to 'Served' -> Completion popup covers patient's screen.

---

## 5. CODING

### a. SQL Commands
Using SQLAlchemy ORM, actual SQL table generation behaves similarly to:
```sql
CREATE TABLE clinics (
    id INTEGER NOT NULL, 
    name VARCHAR(200) NOT NULL, 
    location VARCHAR(500) NOT NULL, 
    PRIMARY KEY (id)
);

CREATE TABLE patients (
    id INTEGER NOT NULL, 
    name VARCHAR(200) NOT NULL, 
    phone_number VARCHAR(10) NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (phone_number)
);

CREATE TABLE doctors (
    id INTEGER NOT NULL, 
    name VARCHAR(200) NOT NULL, 
    specialization VARCHAR(200) NOT NULL, 
    licence_number VARCHAR(20), 
    clinic_id INTEGER NOT NULL, 
    opd_start_time VARCHAR(10) NOT NULL, 
    opd_end_time VARCHAR(10) NOT NULL, 
    status VARCHAR(20) NOT NULL, 
    current_token_number INTEGER NOT NULL, 
    api_key VARCHAR(100) NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(clinic_id) REFERENCES clinics (id), 
    UNIQUE (api_key)
);
```
```

### b. Complete Project Coding (Logic Explanations)
**Frontend Integration:**
In `queue_status.html`, an asynchronous JavaScipt function queries `/api/current_token/<doctor_id>` continuously. 
```javascript
async function fetchQueueStatus() {
    const res = await fetch(`/api/current_token/${doctorId}`);
    const data = await res.json();
    
    // Calculates wait time
    let ahead = Math.max(0, parseInt(myToken) - data.current_token_number - 1);
    let waitEstimates = Math.round(ahead * data.average_consultation_time);
    
    document.getElementById('estimatedWait').innerText = waitEstimates + ' min';
}
```
**Backend API Processing (`doctor_routes.py`):**
When a doctor executes "Mark Done", the backend specifically retrieves the oldest unresolved token associated with that doctor for the current day.
```python
@doctor_bp.route('/doctor/mark_done', methods=['POST'])
def mark_done():
    doctor = Doctor.query.get(data['doctor_id'])
    
    # Extract the oldest waiting token
    current_token = doctor.get_current_token()
    
    # Modifies properties based on system time and state
    current_token.status = 'served'
    current_token.served_at = datetime.now()
    doctor.current_token_number = current_token.token_number
    
    db.session.commit()
    return jsonify({'served_token': current_token.token_number}), 200
```
CareQueue leverages real-world operational mathematics to figure out `average_consultation_time`. The `models.py` logic isolates tokens that have a `served_at` parameter, sorts them by timestamp, limits logical outliers (e.g., > 60 min bounds indicative of breaks), averages the spans between tokens, and serves this float dynamically to the patient.

### c. Code Description
The project consists of specific Python routines:
1.  **get_effective_status():** This module in `Doctor` compares Python's `datetime.now()` string-format against `opd_start_time` and `opd_end_time`. If the time falls outside the bounds, it automatically returns "Closed" regardless of the doctor's manual state, ensuring absolute accuracy.
2.  **generate_token():** Found in `patient_routes.py`. It explicitly verifies if the doctor is currently accepting patients via `doctor.get_effective_status()`. If false, fails with a 400 error. Otherwise, assigns `token_number` and links `patient_id` and `doctor_id`.
3.  **Local Storage Usage:** Once login is successful via `/api/register_patient`, JavaScript writes the ID via `localStorage.setItem('patientId', id)`. This allows state persistence across `queue_status.html` and `select_clinic.html` without burdensome cookies or heavy JWTs.

---

## 6. STANDARDIZATION OF CODING

*   **Naming Conventions:** Variables and database elements stringently follow `snake_case` in Python (e.g., `phone_number`, `get_average_consultation_time`). Frontend JavaScript strictly utilizes `camelCase` (e.g., `fetchQueueStatus`, `myToken`). Class models utilize `PascalCase` (e.g., `Doctor`, `Patient`).
*   **Code Efficiency:** To limit excessive calculations during user polling, statistical queries like `waiting_count` are encapsulated into ORM functions using optimized `db.session.query(...).count()`, ensuring only scalar returns rather than loading massive Python list objects.
*   **Error Handling:** Every Flask Route incorporates explicit `try-except` blocks. In the event of an anomaly (e.g., attempting to generate a token for an invalid doctor), `db.session.rollback()` is fired to prevent internal database locks, followed by returning standard HTTP statuses (400, 404, 500) accompanied by descriptive JSON.
*   **Parameter Passing:** Flask dynamically absorbs route parameters (e.g., `<int:doctor_id>`) securely preventing SQL-injection vulnerabilities inherent in raw query concatenation. 
*   **Validation Checks:** The frontend implements `maxlength="10"` and regex `.replace(/\D/g, "")` to prohibit alphabet chars. The backend verifies data presence using Python conditional checks prior to db commitment.

---

## 7. TESTING

**Testing Techniques Used:**
1.  **Black Box Testing:** Tested the interface inputs without looking at the internal structure. Verified that pressing "Join Queue" while not logged in successfully redirected to `/patient_login`.
2.  **White Box Testing:** Verified the `get_effective_status` bounds testing inside `models.py` to ensure it properly returned "Closed" exactly at boundary times like 12:00.

**Testing Strategy:**
Focus lay entirely on the integration between the Fetch API frontend and Flask backend. Tested behavior heavily over network simulation tools to ensure loading spinners disappeared appropriately.

**Testing Plan & Reports:**
*   *Test 1 (Mobile View):* Scaled screen down to 360px width. Verified `select_clinic.html` stacked correctly. Result: PASS.
*   *Test 2 (Queue Empty Logic):* Attempted to increment "Mark Done" when queue is empty. Expected: API gracefully returns "Queue is empty". Result: PASS.
*   *Test 3 (Completion Modal):* Served token #12 while logged in as user token #12. Expected: Overlay loads displaying "Token Served!". Result: PASS.

**Debugging and Improvements:**
During testing, initial queue updates required manual reloads. By debugging user interaction, it became clear manual refreshing is poor UX. We subsequently implemented a 10s JS `setInterval` that actively polls `/api/current_token/`, drastically improving quality.

---

## 8. SYSTEM SECURITY MEASURES

*   **Data Security:** Data interactions happen via RESTful methodologies communicating JSON blocks. Cross-Origin Resource Sharing (CORS) is explicitly implemented to manage API endpoint access parameters. Database configurations avoid tracking modifications directly to minimize metadata sniffing.
*   **User Authentication:** Patient identity is tied directly to unique mobile phone strings. During generation, foreign key constraints rigorously ensure only validated IDs exist in relations. Doctor routing implements a secure `licence_number` tracking methodology during login.
*   **Access Control:** To delete a clinic layout (`/api/doctor/delete`), strict JSON payloads are necessitated, assuring arbitrary browsers cannot manipulate database deletions. The frontend utilizes `localStorage` mapping, enforcing a login gateway before permitting `queue_status` access.

---

## 9. COST ESTIMATION

As an academic project built upon open-source fundamentals, software costs are drastically minimized.
| Resource | Tool Used | Estimated Cost Setup | Total Software Cost |
| :--- | :--- | :--- | :--- |
| **Backend OS / Stack** | Python, Flask | $0 | $0 |
| **Relational DB**| SQLite3 | $0 | $0 |
| **Text Editor / IDE** | Visual Studio Code | $0 | $0 |
| **Hosting (Proposed)**| Render (Free Tier) | $0/month | $0 |

Assuming manual labor hours for commercial deployment based on 100 development hours at a rudimentary academic valuation of \$20/hour, the approximate theoretical project cost translates to **$2,000**. Production deployment requiring a persistent PostgreSQL cloud instance could scale slightly ($10-$20/month).

---

## 10. REPORTS

**Sample Output Layouts Produced:**

*Queue Status Interface Breakdown:*
*   Header: Valid Clinic Name + Verified Doctor Name.
*   Blinking 'LIVE' indicator.
*   Center Output: Custom "Token Number".
*   Row Fields: [Current Serving], [Patients Ahead], [Estimated Wait].
*   Data represents fetched attributes formatted logically.

*Doctor Dashboard Interface Breakdown:*
*   Header: Status Open/Break/Closed (color coordinated).
*   Center Output: Total distinct waiting patients, and raw current token.
*   Sub-section: Computed Avg. Consultation Time formatting float metrics.

*(See application instance for true visual rendering representations).*

---

## 11. FUTURE SCOPE 

The architectural flexibility of CareQueue provisions extensive enhancements:
*   **Mobile App Iteration:** Transitioning the Vanilla JS frontend into React Native to leverage native Push Notifications rather than periodic HTTP polling.
*   **WebSockets:** Re-writing the Flask architecture to support `Socket.io` allowing instantaneous real-time updates directly piped to the client without needing a 10-second polling interval.
*   **Analytics Panel for Clinics:** Building advanced data visualization screens to highlight peak weekly queue timings, overall doctor efficiency, and patient recidivism.
*   **SMS Integration:** Employing robust APIs like Twilio to actively text users 15 minutes prior to their designated appointment slot.

---

## 12. BIBLIOGRAPHY

1.  Grinberg, Miguel. *Flask Web Development: Developing Web Applications with Python.* O'Reilly Media. 
2.  SQLAlchemy Documentation. Object Relational Tutorial (1.x API). Available at: https://docs.sqlalchemy.org/
3.  Mozilla Developer Network (MDN) Web Docs. JavaScript Fetch API Guide. Available at: https://developer.mozilla.org/

---

## 13. APPENDICES

**Appendix A: Application Structure**
```text
Care Queue/
  ├── backend/
  │    ├── app.py
  │    ├── database.py
  │    ├── models.py
  │    ├── seed_data.py
  │    └── routes/ (clinic, doctor, patient)
  ├── Frontend/
  ├── static/ (css, js)
  └── templates/ (html implementations)
```

**Appendix B: Test Data Generation**
A robust testing environment was supplied via `seed_data.py`, instantiating 3 clinics ("Vital Wave Rehabs", "Share & Heal", "Health Care"), attaching mock practitioners ("Dr. Hetvi Rathod"), generating randomly secured 32-bit API Keys, and initializing backdated tokens to pre-calculate mathematical wait-times effectively.

---

## 14. GLOSSARY

*   **API (Application Programming Interface):** The backend interface facilitating logical transactions between the front-side JS and the SQLite server.
*   **CORS (Cross-Origin Resource Sharing):** Security feature managed within Flask explicitly allowing frontend HTML to issue HTTP calls successfully.
*   **DB (Database):** The systematic SQLite instance capturing all relational bindings (carequeue.db).
*   **DFD (Data Flow Diagram):** Diagrammatically mapping input interactions from the interface through backend processing modules.
*   **OPD (Outpatient Department):** The fundamental real-world clinic operations being emulated.
*   **ORM (Object-Relational Mapping):** The mechanism binding raw database SQL queries safely into manageable Python class arrays.
*   **SRS:** Standardized documentation highlighting what physical capacities the final design structurally accommodates.
*   **Token:** A unique incremented integer logically granting queue prioritization order.

---
*End of Report.*
