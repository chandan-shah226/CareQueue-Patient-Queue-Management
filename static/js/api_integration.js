/**
 * CareQueue API Integration Library
 * 
 * This file provides JavaScript functions to interact with the Flask backend API.
 * Use these functions in your HTML files to connect buttons and forms to the backend.
 * 
 * All functions use fetch() for HTTP requests and return Promises.
 * 
 * USAGE EXAMPLES:
 * 
 * 1. Register Patient (Login Page):
 *    registerPatient('9876543210', 'John Doe')
 *      .then(data => console.log('Patient:', data.patient))
 *      .catch(error => console.error(error));
 * 
 * 2. Generate Token (Join Queue Button):
 *    generateToken(patientId, doctorId)
 *      .then(data => alert(`Your token: #${data.token.token_number}`))
 *      .catch(error => console.error(error));
 * 
 * 3. Get Current Token (Display on Clinic Page):
 *    getCurrentToken(doctorId)
 *      .then(data => displayToken(data.current_token))
 *      .catch(error => console.error(error));
 */

// Base URL for the API (change if backend is on different port)
const API_BASE_URL = '/api';


/**
 * Register a patient or get existing patient by phone number
 * 
 * @param {string} phoneNumber - 10-digit phone number
 * @param {string} name - Patient name (optional, defaults to 'Guest')
 * @returns {Promise} Promise resolving to patient data
 * 
 * Response Format:
 * {
 *   message: "Patient registered successfully",
 *   patient: {
 *     id: 1,
 *     name: "John Doe",
 *     phone_number: "9876543210"
 *   }
 * }
 */
async function registerPatient(phoneNumber, name = 'Guest') {
    try {
        const response = await fetch(`${API_BASE_URL}/register_patient`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                phone_number: phoneNumber,
                name: name
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to register patient');
        }
        
        return data;
    } catch (error) {
        console.error('Error registering patient:', error);
        throw error;
    }
}


/**
 * Generate a queue token for a patient
 * 
 * @param {number} patientId - Patient ID from registration
 * @param {number} doctorId - Doctor ID to join queue for
 * @returns {Promise} Promise resolving to token data
 * 
 * Response Format:
 * {
 *   message: "Token generated successfully",
 *   token: {
 *     id: 1,
 *     token_number: 5,
 *     status: "waiting",
 *     doctor_name: "Dr. Smith",
 *     created_at: "2026-02-11T22:30:00"
 *   },
 *   queue_position: 3
 * }
 */
async function generateToken(patientId, doctorId) {
    try {
        const response = await fetch(`${API_BASE_URL}/generate_token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                patient_id: patientId,
                doctor_id: doctorId
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to generate token');
        }
        
        return data;
    } catch (error) {
        console.error('Error generating token:', error);
        throw error;
    }
}


/**
 * Get the current active token for a doctor
 * 
 * @param {number} doctorId - Doctor ID
 * @returns {Promise} Promise resolving to current token data
 * 
 * Response Format:
 * {
 *   doctor_id: 1,
 *   doctor_name: "Dr. Smith",
 *   current_token: {
 *     token_number: 5,
 *     patient_name: "John Doe",
 *     status: "waiting"
 *   },
 *   waiting_count: 7
 * }
 */
async function getCurrentToken(doctorId) {
    try {
        const response = await fetch(`${API_BASE_URL}/current_token/${doctorId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to get current token');
        }
        
        return data;
    } catch (error) {
        console.error('Error getting current token:', error);
        throw error;
    }
}


/**
 * Mark current token as completed (Doctor action - requires API key)
 * 
 * @param {number} doctorId - Doctor ID
 * @param {string} apiKey - Doctor's API key
 * @returns {Promise} Promise resolving to completion data
 * 
 * Response Format:
 * {
 *   message: "Token completed successfully",
 *   completed_token: {
 *     token_number: 5,
 *     patient_name: "John Doe"
 *   },
 *   next_token: {
 *     token_number: 6,
 *     patient_name: "Jane Smith"
 *   },
 *   waiting_count: 6
 * }
 */
async function completeToken(doctorId, apiKey) {
    try {
        const response = await fetch(`${API_BASE_URL}/complete_token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': apiKey  // API key authentication
            },
            body: JSON.stringify({
                doctor_id: doctorId
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to complete token');
        }
        
        return data;
    } catch (error) {
        console.error('Error completing token:', error);
        throw error;
    }
}


/**
 * Get all waiting tokens for a doctor (full queue view)
 * 
 * @param {number} doctorId - Doctor ID
 * @returns {Promise} Promise resolving to queue data
 * 
 * Response Format:
 * {
 *   doctor_id: 1,
 *   doctor_name: "Dr. Smith",
 *   waiting_tokens: [
 *     {
 *       token_number: 5,
 *       patient_name: "John Doe",
 *       created_at: "2026-02-11T10:30:00"
 *     },
 *     ...
 *   ],
 *   total_waiting: 7
 * }
 */
async function getDoctorQueue(doctorId) {
    try {
        const response = await fetch(`${API_BASE_URL}/doctor_queue/${doctorId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to get doctor queue');
        }
        
        return data;
    } catch (error) {
        console.error('Error getting doctor queue:', error);
        throw error;
    }
}


/**
 * Get all clinics with doctors and queue statistics
 * 
 * @returns {Promise} Promise resolving to clinics data
 * 
 * Response Format:
 * {
 *   clinics: [
 *     {
 *       id: 1,
 *       name: "Vital Wave Rehabs",
 *       location: "Jamnagar",
 *       doctors: [
 *         {
 *           id: 1,
 *           name: "Dr. Hetvi Rathod",
 *           specialization: "Physiotherapy",
 *           current_token: "#5",
 *           waiting_count: 3
 *         }
 *       ]
 *     }
 *   ],
 *   total_clinics: 3
 * }
 */
async function getAllClinics() {
    try {
        const response = await fetch(`${API_BASE_URL}/clinics`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to get clinics');
        }
        
        return data;
    } catch (error) {
        console.error('Error getting clinics:', error);
        throw error;
    }
}


/**
 * Get specific clinic details
 * 
 * @param {number} clinicId - Clinic ID
 * @returns {Promise} Promise resolving to clinic data
 * 
 * Response Format:
 * {
 *   id: 1,
 *   name: "Vital Wave Rehabs",
 *   location: "Jamnagar",
 *   doctors: [
 *     {
 *       id: 1,
 *       name: "Dr. Hetvi Rathod",
 *       specialization: "Physiotherapy",
 *       current_token: "#5",
 *       waiting_count: 3
 *     }
 *   ]
 * }
 */
async function getClinicDetails(clinicId) {
    try {
        const response = await fetch(`${API_BASE_URL}/clinic/${clinicId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to get clinic details');
        }
        
        return data;
    } catch (error) {
        console.error('Error getting clinic details:', error);
        throw error;
    }
}


// ============================================================================
// INTEGRATION EXAMPLES FOR YOUR HTML FILES
// ============================================================================

/**
 * EXAMPLE 1: Login Button Integration (index.html)
 * 
 * Replace your existing login button handler with this:
 */
function exampleLoginIntegration() {
    const loginBtn = document.getElementById("loginBtn");
    const phoneInput = document.getElementById("phone");
    
    loginBtn.addEventListener("click", async function () {
        if (loginBtn.classList.contains("active")) {
            const phoneNumber = phoneInput.value;
            
            try {
                // Register patient
                const result = await registerPatient(phoneNumber, 'Guest User');
                
                // Store patient ID in localStorage for later use
                localStorage.setItem('patientId', result.patient.id);
                localStorage.setItem('phoneNumber', result.patient.phone_number);
                
                // Navigate to clinic selection
                window.location.href = "select_clinic";
            } catch (error) {
                alert('Login failed: ' + error.message);
            }
        }
    });
}


/**
 * EXAMPLE 2: Join Queue Button Integration (clinic_details.html)
 * 
 * Add this to handle the "Join Queue" button:
 */
function exampleJoinQueueIntegration() {
    const joinBtn = document.querySelector(".join-btn");
    
    joinBtn.addEventListener("click", async function () {
        // Get patient ID from localStorage (set during login)
        const patientId = localStorage.getItem('patientId');
        
        // Get doctor ID from URL or page data
        const params = new URLSearchParams(window.location.search);
        const clinicId = parseInt(params.get("id"));
        
        // For now, assuming first doctor of the clinic (you can modify this)
        // You'll need to fetch clinic details first to get the doctor ID
        
        try {
            const clinic = await getClinicDetails(clinicId);
            const doctorId = clinic.doctors[0].id;  // First doctor
            
            // Generate token
            const result = await generateToken(patientId, doctorId);
            
            alert(`Success! Your token number is #${result.token.token_number}`);
        } catch (error) {
            alert('Failed to join queue: ' + error.message);
        }
    });
}


/**
 * EXAMPLE 3: Load Clinic Data Dynamically (select_clinic.html)
 * 
 * Replace the hardcoded clinic data with live API data:
 */
async function exampleLoadClinics() {
    try {
        const result = await getAllClinics();
        
        // Now you can use result.clinics to populate your UI
        result.clinics.forEach(clinic => {
            console.log(clinic.name, clinic.doctors);
            // Update your HTML elements here
        });
    } catch (error) {
        console.error('Failed to load clinics:', error);
    }
}
