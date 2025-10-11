# appointments.py
import streamlit as st

# Initialize session state for appointments (to persist during session)
if "appointments" not in st.session_state:
    st.session_state["appointments"] = []

def book_appointment(patient_id, doctor_name, time_slot, symptom=None):
    appt = {
        "patient": patient_id,
        "doctor": doctor_name,
        "slot": time_slot,
        "symptom": symptom,
        "status": "Pending"
    }
    st.session_state["appointments"].append(appt)
    return appt

def get_patient_appointments(patient_id):
    return [a for a in st.session_state["appointments"] if a["patient"] == patient_id]

def get_doctor_appointments(doctor_name):
    return [a for a in st.session_state["appointments"] if a["doctor"] == doctor_name]

def update_appointment_status(doctor_name, idx, status):
    appts = get_doctor_appointments(doctor_name)
    if 0 <= idx < len(appts):
        appts[idx]["status"] = status
        return True
    return False
