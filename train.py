import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pandas as pd

# Load dataset
data = pd.read_csv("symptoms_dataset.csv")   # <-- your dataset here
X = data["symptom"]
y = data["category"]

# Convert text to numbers
vectorizer = TfidfVectorizer()
X_vectorized = vectorizer.fit_transform(X)

# Train model
model = LogisticRegression()
model.fit(X_vectorized, y)

# Save model & vectorizer
joblib.dump(model, "medbot_model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("✅ Model trained and saved successfully")