import sqlite3
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

DB_PATH = "weather.db"


def main():
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        """
        SELECT location, humidity, pressure, wind_speed,
               rain_probability, uv_index, timestamp, temperature
        FROM weather
        WHERE temperature IS NOT NULL
        ORDER BY location, timestamp
        """,
        conn
    )

    conn.close()

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Time features
    df["hour"] = df["timestamp"].dt.hour
    df["day"] = df["timestamp"].dt.day
    df["month"] = df["timestamp"].dt.month

    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

    # Historical temperature features per city
    grouped = df.groupby("location")["temperature"]

    df["temp_lag_1"] = grouped.shift(1)
    df["temp_lag_3"] = grouped.shift(3)
    df["temp_lag_6"] = grouped.shift(6)
    df["temp_lag_24"] = grouped.shift(24)

    df["temp_roll_6"] = (
        df.groupby("location")["temperature"]
        .transform(lambda x: x.shift(1).rolling(6).mean())
    )

    df["temp_roll_24"] = (
        df.groupby("location")["temperature"]
        .transform(lambda x: x.shift(1).rolling(24).mean())
    )

    df = df.dropna()

    features = [
        "humidity",
        "pressure",
        "wind_speed",
        "rain_probability",
        "uv_index",
        "hour",
        "day",
        "month",
        "hour_sin",
        "hour_cos",
        "month_sin",
        "month_cos",
        "temp_lag_1",
        "temp_lag_3",
        "temp_lag_6",
        "temp_lag_24",
        "temp_roll_6",
        "temp_roll_24",
    ]

    # City-wise chronological split
    train_parts = []
    test_parts = []

    for city, city_df in df.groupby("location"):
        city_df = city_df.sort_values("timestamp")

        split = int(len(city_df) * 0.8)

        train_parts.append(city_df.iloc[:split])
        test_parts.append(city_df.iloc[split:])

    train_df = pd.concat(train_parts)
    test_df = pd.concat(test_parts)

    X_train = train_df[features]
    y_train = train_df["temperature"]

    X_test = test_df[features]
    y_test = test_df["temperature"]

    # Train model
    model = RandomForestRegressor(
        n_estimators=150,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5
    r2 = r2_score(y_test, predictions)

    print("\n📊 CITY-WISE TIME-BASED EVALUATION")
    print("--------------------------------------")
    print(f"Dataset size : {len(df)}")
    print(f"Training data: {len(train_df)}")
    print(f"Test data    : {len(test_df)}")
    print(f"Cities       : {df['location'].nunique()}")
    print(f"MAE          : {mae:.2f} °C")
    print(f"RMSE         : {rmse:.2f} °C")
    print(f"R² Score     : {r2:.3f}")
    print("--------------------------------------")


if __name__ == "__main__":
    main()