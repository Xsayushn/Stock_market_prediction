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

    return RandomForestRegressor(n_estimators=300, random_state=42)

def rmse(y_true, y_pred):
    return float(np.sqrt(((y_true - y_pred) ** 2).mean()))
