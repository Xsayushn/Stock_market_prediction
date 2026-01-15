def forecast_next_days(model, last_features_row, days=7):
    preds = []
    current = last_features_row.copy()

    for _ in range(days):
        nxt = model.predict([current])[0]
        preds.append(float(nxt))
        current[0] = nxt  # update Close feature only (simple iterative forecast)

    return preds
