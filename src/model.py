import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

MODEL_PATH = "models/stock_model.pkl"

def train_model(X_train, y_train):
    model = RandomForestRegressor(
        n_estimators=400,
        random_state=42
    )
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, pred)
    rmse = np.sqrt(mean_squared_error(y_test, pred))
    return pred, mae, rmse

def save_model(model):
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)

def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

def predict_next_days(model, last_row_features, days=7):
    """
    Simple multi-step forecast:
    uses previous prediction as next day's Close (approx)
    """
    preds = []
    current = last_row_features.copy()

    for _ in range(days):
        next_price = model.predict([current])[0]
        preds.append(next_price)

        # Update only Close feature for next step (simple approximation)
        current[0] = next_price

    return preds
