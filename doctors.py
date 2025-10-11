import json

with open("doctors.json", "r") as f:
    doctor_data = json.load(f)

def recommend_doctor(symptom_category):
    """Return list of doctor names matching the symptom category"""
    recommended = [d["name"] for d in doctor_data if symptom_category.lower() in d["specialty"].lower()]
    return recommended if recommended else [d["name"] for d in doctor_data]

def get_doctor_list():
    """Return list of all doctor names"""
    return [d["name"] for d in doctor_data]
