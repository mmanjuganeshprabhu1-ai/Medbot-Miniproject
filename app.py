import streamlit as st

import joblib

import json

import pandas as pd

import random

from sklearn.preprocessing import LabelEncoder

import os



# -----------------------------

# --- Load Files (Your Colab Model + JSONs) ---

# -----------------------------

try:

    model = joblib.load("medbot_model.pkl")

    vectorizer = joblib.load("vectorizer.pkl")



    with open("intents.json") as f:

        intents = json.load(f)



    with open("doctors.json") as f:

        doctors = json.load(f)



    with open("symptoms.json") as f:

        symptoms = json.load(f)



    doctors_df = pd.DataFrame(doctors)



    le = LabelEncoder()

    tags = [intent['tag'] for intent in intents['intents']]

    le.fit(tags)



except FileNotFoundError as e:

    st.error(f"Missing file: {e}. Place your Colab files (medbot_model.pkl, vectorizer.pkl) and JSONs in the folder.")

    st.stop()

except Exception as e:

    st.error(f"Error loading: {e}. Check if JSONs match your model tags.")

    st.stop()



# -----------------------------

# --- Demo Users (Customize if Needed) ---

# -----------------------------

users = {

    "patient_user": {"password": "patient_pass", "role": "Patient"},

    "doctor_user": {"password": "doctor_pass", "role": "Doctor"},

    "admin_user": {"password": "admin_pass", "role": "Admin"}

}



# -----------------------------

# --- Specialty Map (Matches Symptoms to Doctors) ---

# -----------------------------

specialty_map = {

    "fever": "General Physician", "cough": "General Physician", "cold": "ENT",

    "headache": "Neurologist", "back pain": "Orthopedic", "stomach pain": "Gastroenterologist",

    "nausea": "Gastroenterologist", "vomiting": "Gastroenterologist", "chest pain": "Cardiologist",

    "shortness of breath": "Cardiologist", "allergy": "ENT", "sore throat": "ENT"

}



# -----------------------------

# --- Functions ---

# -----------------------------

def get_bot_response(user_input):

    user_input_vec = vectorizer.transform([user_input.lower()])

    prediction = model.predict(user_input_vec)

    predicted_tag = le.inverse_transform(prediction)[0]

    for intent in intents['intents']:

        if intent['tag'] == predicted_tag:

            return random.choice(intent['responses']), predicted_tag

    return "Sorry, I don't understand. Please describe your symptom clearly.", None



def recommend_doctors(symptom, top_n=3):

    specialties = specialty_map.get(symptom, "General Physician")

    if isinstance(specialties, str):

        specialties = [specialties]

    filtered_docs = doctors_df[doctors_df['specialty'].isin(specialties)]

    sorted_docs = filtered_docs.sort_values(by='rating', ascending=False)

    top_docs = []

    for _, row in sorted_docs.head(top_n).iterrows():

        slots_str = row['slots']

        slots = [s.strip() for s in slots_str.split(',')] if isinstance(slots_str, str) else slots_str

        top_docs.append({

            "name": row['name'],

            "specialty": row['specialty'],

            "rating": row['rating'],

            "slots": slots

        })

    return top_docs



def book_appointment(patient_id, doctor_name, time_slot, symptom):

    appt = {

        "patient": patient_id,

        "doctor": doctor_name,

        "time": time_slot,

        "symptom": symptom,

        "status": "Pending"

    }

    st.session_state.appointments.append(appt)

    return appt



def get_patient_appointments(patient_id):

    return [a for a in st.session_state.appointments if a["patient"] == patient_id]



def get_doctor_appointments(doctor_id):

    return [a for a in st.session_state.appointments if a["doctor"] == doctor_id]



# -----------------------------

# --- Initialize Session State ---

# -----------------------------

if 'logged_in' not in st.session_state:

    st.session_state.logged_in = False

if 'role' not in st.session_state:

    st.session_state.role = None

if 'username' not in st.session_state:

    st.session_state.username = None

if 'chat_history' not in st.session_state:

    st.session_state.chat_history = []

if 'current_symptom' not in st.session_state:

    st.session_state.current_symptom = None

if 'follow_up_questions' not in st.session_state:

    st.session_state.follow_up_questions = []

if 'follow_up_index' not in st.session_state:

    st.session_state.follow_up_index = 0

if 'follow_up_answers' not in st.session_state:

    st.session_state.follow_up_answers = {}

if 'asking_follow_up' not in st.session_state:

    st.session_state.asking_follow_up = False

if 'symptoms_collected' not in st.session_state:

    st.session_state.symptoms_collected = []

if 'appointments' not in st.session_state:

    st.session_state.appointments = []



# -----------------------------

# --- Login Section ---

# -----------------------------

st.title("🩺 MedBot Healthcare Assistant")



if not st.session_state.logged_in:

    st.subheader("Login")

    col1, col2 = st.columns([1, 2])

    with col1:

        user_type = st.selectbox("Login as", ["Patient", "Doctor", "Admin"])

    with col2:

        username = st.text_input("Username")

        password = st.text_input("Password", type="password")



    if st.button("Login"):

        if username in users and users[username]["password"] == password and users[username]["role"] == user_type:

            st.session_state.logged_in = True

            st.session_state.username = username

            st.session_state.role = user_type

            st.success(f"Welcome, {username}!")

            st.rerun()

        else:

            st.error("Invalid credentials. Demos: patient_user/patient_pass (Patient), doctor_user/doctor_pass (Doctor), admin_user/admin_pass (Admin).")



    st.info("Demo Logins:\n- Patient: patient_user / patient_pass\n- Doctor: doctor_user / doctor_pass\n- Admin: admin_user / admin_pass")

else:

    st.sidebar.success(f"Logged in as: {st.session_state.username} ({st.session_state.role})")

    if st.sidebar.button("Logout"):

        for key in list(st.session_state.keys()):

            del st.session_state[key]

        st.rerun()



# -----------------------------

# --- Patient Dashboard ---

# -----------------------------

if st.session_state.logged_in and st.session_state.role == "Patient":

    st.subheader(f"Welcome, {st.session_state.username}!")



    # Clear Chat Button

    if st.button("Clear Chat"):

        st.session_state.chat_history = []

        st.session_state.current_symptom = None

        st.session_state.asking_follow_up = False

        st.session_state.follow_up_index = 0

        st.session_state.follow_up_answers = {}

        st.session_state.symptoms_collected = []

        st.rerun()



    st.markdown("### 💬 Chat with MedBot")



    # Display Chat History

    for chat in st.session_state.chat_history:

        if chat.get('user'):

            st.write(f"*You:* {chat['user']}")

        if chat.get('bot'):

            st.write(f"*MedBot:* {chat['bot']}")



    # Follow-up Questions

    if st.session_state.asking_follow_up:

        idx = st.session_state.follow_up_index

        if idx < len(st.session_state.follow_up_questions):

            question = st.session_state.follow_up_questions[idx]

            answer = st.text_input(f"Your answer to: {question}", key=f"fu_{idx}")

            if st.button("Submit", key=f"sub_{idx}") and answer.strip():

                st.session_state.chat_history.append({"user": answer, "bot": None})

                st.session_state.follow_up_answers[question] = answer

                st.session_state.follow_up_index += 1

                st.rerun()

        else:

            # End Follow-ups, Proceed to Recommendations

            st.session_state.asking_follow_up = False

            summary = f"Thanks for details on {st.session_state.current_symptom}. Here's recommendations based on your symptoms and doctor ratings."

            st.session_state.chat_history.append({"user": None, "bot": summary})

            st.session_state.symptoms_collected.append(st.session_state.current_symptom)

            st.session_state.current_symptom = None

            st.rerun()



    # Initial Symptom Input

    if not st.session_state.asking_follow_up and st.session_state.current_symptom is None:

        user_input = st.text_input("Describe your symptom (e.g., 'I have a fever'):")

        if st.button("Send") and user_input.strip():

            st.session_state.chat_history.append({"user": user_input, "bot": None})

            bot_response, predicted_symptom = get_bot_response(user_input)

            st.session_state.chat_history[-1]["bot"] = bot_response

            if predicted_symptom and predicted_symptom in symptoms:

                st.session_state.current_symptom = predicted_symptom

                st.session_state.asking_follow_up = True

                st.session_state.follow_up_index = 0

                st.session_state.follow_up_answers = {}

                symptom_intent = next((i for i in intents['intents'] if i['tag'] == predicted_symptom), None)

                st.session_state.follow_up_questions = symptom_intent.get('follow_up', []) if symptom_intent else []

                if st.session_state.follow_up_questions:

                    first_q = st.session_state.follow_up_questions[0]

                    st.session_state.chat_history.append({"user": None, "bot": first_q})

                else:

                    # No follow-ups, directly recommend

                    summary = f"Based on {predicted_symptom}, here are recommendations."

                    st.session_state.chat_history.append({"user": None, "bot": summary})

                    st.session_state.symptoms_collected.append(predicted_symptom)

                    st.session_state.current_symptom = None

                st.rerun()

            else:

                st.session_state.chat_history.append({"user": None, "bot": "I couldn't identify the symptom. Try again with clearer description."})

                st.rerun()



    # Recommendations and Booking (after symptoms collected)

    if st.session_state.symptoms_collected:

        st.markdown("### 👨‍⚕ Recommended Doctors (Top 3 by Rating)")

        symptom = st.session_state.symptoms_collected[-1]  # Use latest symptom

        top_docs = recommend_doctors(symptom)

        if top_docs:

            for i, doc in enumerate(top_docs, 1):

                st.write(f"{i}. *{doc['name']}* ({doc['specialty']}) - Rating: ⭐ {doc['rating']}")

            

            choice = st.number_input("Select doctor number (1-3):", min_value=1, max_value=len(top_docs), step=1)

            selected_doc = top_docs[int(choice) - 1]

            time_slot = st.selectbox("Choose available time slot:", selected_doc['slots'])



            if st.button("Book Appointment"):

                if time_slot:

                    appt = book_appointment(st.session_state.username, selected_doc["name"], time_slot, symptom)

                    st.success(f"✅ Appointment booked! Waiting for {selected_doc['name']}'s confirmation. Status: Pending.")

                    st.rerun()

                else:

                    st.warning("Please select a time slot.")

        else:

            st.warning("No doctors available for this symptom.")



    # Show Patient Appointments (Pending/Accepted/Rejected)

    st.markdown("### 📅 Your Appointments (Waiting for Doctor Confirmation)")

    appts = get_patient_appointments(st.session_state.username)

    if appts:

        for a in appts:

            status_emoji = "⏳" if a["status"] == "Pending" else "✅" if a["status"] == "Accepted" else "❌"

            st.write(f"{status_emoji} *Doctor:* {a['doctor']} | *Symptom:* {a['symptom']} | *Time:* {a['time']} | *Status:* {a['status']}")

    else:

        st.info("No appointments booked yet. Start a chat to book one!")



# -----------------------------

# --- Doctor Dashboard ---

# -----------------------------

elif st.session_state.logged_in and st.session_state.role == "Doctor":

    st.subheader(f"Welcome, Dr. {st.session_state.username}!")



    st.markdown("### 🗓 Your Pending Appointments")



    appts = get_doctor_appointments(st.session_state.username)

    if appts:

        for idx, a in enumerate(appts):

            status_emoji = "⏳" if a["status"] == "Pending" else "✅" if a["status"] == "Accepted" else "❌"

            st.write(f"{status_emoji} *Patient:* {a['patient']} | *Symptom:* {a['symptom']} | *Time:* {a['time']} | *Status:* {a['status']}")

            if a["status"] == "Pending":

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(f"Accept Appointment {idx+1}", key=f"accept_{idx}"):

                        a["status"] = "Accepted"

                        st.success(f"Accepted appointment for {a['patient']}!")

                        st.rerun()

                with col2:

                    if st.button(f"Reject Appointment {idx+1}", key=f"reject_{idx}"):

                        a["status"] = "Rejected"

                        st.warning(f"Rejected appointment for {a['patient']}.")

                        st.rerun()

    else:

        st.info("No pending appointments. Check back later!")



# -----------------------------

# --- Admin Dashboard ---

# -----------------------------

elif st.session_state.logged_in and st.session_state.role == "Admin":

    st.subheader("Admin Dashboard")



    st.markdown("### 📋 All Appointments")

    if st.session_state.appointments:

        for a in st.session_state.appointments:

            status_emoji = "⏳" if a["status"] == "Pending" else "✅" if a["status"] == "Accepted" else "❌"

            st.write(f"{status_emoji} *Patient:* {a['patient']} | *Doctor:* {a['doctor']} | *Symptom:* {a['symptom']} | *Time:* {a['time']} | *Status:* {a['status']}")

    else:

        st.info("No appointments in the system yet.")



    st.markdown("### 👨‍⚕ All Doctors Overview")

    if not doctors_df.empty:

        st.dataframe(doctors_df, use_container_width=True)

    else:

        st.warning("No doctors data loaded.")