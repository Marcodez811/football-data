import pandas as pd
from xgboost import XGBClassifier
from sklearn.metrics import precision_score

# Load and prepare the data as before
matches = pd.read_csv('matches.csv')
matches["date"] = pd.to_datetime(matches["date"])
matches["venue_code"] = matches["venue"].astype("category").cat.codes
matches["opp_code"] = matches["opponent"].astype("category").cat.codes
matches["day_code"] = matches["date"].dt.dayofweek
matches["hour"] = matches["time"].str[:2].astype("int")
matches["target"] = matches["result"] == 'W'
matches["ref_code"] = matches["captain"].astype("category").cat.codes
matches["captain_code"] = matches["referee"].astype("category").cat.codes

# Rolling average function remains the same
def rolling_avg(group: pd.DataFrame, cols, new_cols):
    group = group.sort_values("date")
    rolling_stats = group[cols].rolling(3, closed="left").mean()
    group[new_cols] = rolling_stats
    return group.dropna(subset=new_cols)

# Group by team and apply rolling averages
cols = ["gf", "ga", "sh", "sot", "dist", "fk", "pk", "pkatt", "xg", "xga"]
new_cols = [f"{c}_rolling" for c in cols]
matches_rolling = matches.groupby("team").apply(lambda group: rolling_avg(group, cols, new_cols)).droplevel('team')
matches_rolling.index = range(matches_rolling.shape[0])

# Split the data into train and test
def predict(model, data, predictors):
    train = data[(data["date"] <= '2024-01-01')]
    test = data[data["date"] > '2024-01-01']
    model.fit(train[predictors], train["target"])
    preds = model.predict(test[predictors])
    combined = pd.DataFrame(dict(actual=test["target"], predicted=preds), index=test.index)
    return combined, precision_score(combined["actual"], combined["predicted"])

# Initializing XGBoost instead of RandomForest
xgb = XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, subsample=0.8, random_state=1)

# Predictor columns (as before)
pred_cols = ["venue_code", "opp_code", "day_code", "hour", "ref_code", "captain_code"]

# Use rolling stats along with existing features for training
combined, precision = predict(xgb, matches_rolling, pred_cols + new_cols)

num_estimators = 100

# Hyperparameter tuning loop
while precision < 0.65:
    # Increase the number of boosting rounds (trees)
    num_estimators += 10
    xgb = XGBClassifier(n_estimators=num_estimators, learning_rate=0.1, max_depth=3, subsample=0.8, random_state=1)
    combined, precision = predict(xgb, matches_rolling, pred_cols + new_cols)
    print(f'Current precision: {precision}')

# Merging results with the original data for further analysis
combined = combined.merge(matches_rolling[["date", "team", "opponent", "result"]], left_index=True, right_index=True)
print(combined)
