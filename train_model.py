import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os

print("Loading dataset...")

# Load dataset
births = pd.read_csv("births.csv")

# Clean missing values
births['day'] = births['day'].fillna(1).astype(int)

# Features and target
X = births[['year', 'month', 'day']]
y = births['births']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("Training model...")

# Train model
model = RandomForestRegressor(random_state=42)
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Evaluation
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("\n--- Model Performance ---")
print("MAE :", mae)
print("RMSE:", rmse)
print("R2  :", r2)

# Save model in same folder
model_path = os.path.join(os.path.dirname(__file__), "birth_prediction_model.pkl")
joblib.dump(model, model_path)

print("\n Model saved successfully as: birth_prediction_model.pkl")
