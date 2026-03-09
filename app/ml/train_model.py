import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib

# connect to database
conn = sqlite3.connect("weather.db")

# load dataset
df = pd.read_sql_query("SELECT * FROM weather", conn)

# convert timestamp to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

# extract hour feature
df["hour"] = df["timestamp"].dt.hour

# features and target
X = df[["hour", "humidity", "pressure", "wind_speed"]]
y = df["temperature"]

# split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# train model
model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)

# save model
joblib.dump(model, "temperature_model.pkl")

print("Model trained successfully!")