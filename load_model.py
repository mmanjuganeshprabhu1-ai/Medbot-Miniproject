import joblib
import streamlit as st

# Load model & vectorizer once
@st.cache_resource
def load_assets():
    model = joblib.load("medbot_model.pkl")
    vectorizer = joblib.load("vectorizer.pkl")
    return model, vectorizer

model, vectorizer = load_assets()

st.title("💊 MedBot")
user_input = st.text_input("Describe your symptoms:")

if st.button("Predict"):
    if user_input.strip():
        X_test = vectorizer.transform([user_input])
        prediction = model.predict(X_test)[0]
        st.success(f"Predicted Condition: **{prediction}**")
    else:
        st.warning("Please enter some text.")
