import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

def get_model(model_name: str):
    if model_name == "Linear Regression":
        return LinearRegression()

    if model_name == "Random Forest":
        return RandomForestRegressor(
            n_estimators=400,
            random_state=42
        )

    if model_name == "XGBoost (optional)":
        try:
            from xgboost import XGBRegressor
            return XGBRegressor(
                n_estimators=400,
                learning_rate=0.05,
                max_depth=6,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42
            )
        except Exception:
            return None

    if model_name == "LSTM (optional)":
        # We return None here; LSTM is handled differently.
        return "LSTM"

    return RandomForestRegressor(n_estimators=300, random_state=42)

def rmse(y_true, y_pred):
    return float(np.sqrt(((y_true - y_pred) ** 2).mean()))
