import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy.stats import pearsonr
import json

# Load datasets
train_df = pd.read_csv('data/processed/train_data.csv')
test_df = pd.read_csv('data/processed/test_data.csv')

stations = ['hyderabad', 'bangalore', 'lucknow', 'colombo']
horizons = ['1h', '3h', '6h']

# Base features
solar_features = ['xray_flux', 'solar_wind_speed', 'imf_bz', 'kp_index', 'dst_index']
lag_suffixes = ['_lag_1h', '_lag_3h', '_lag_6h', '_lag_12h', '_lag_24h']
lag_features = [f + s for f in solar_features for s in lag_suffixes]
time_features = ['hour_of_day', 'day_of_year']

base_features = solar_features + lag_features + time_features

results = []

print("| Station | Horizon | RMSE | MAE | R |")
print("|---------|---------|------|-----|---|")

for station in stations:
    for horizon in horizons:
        # Station specific feature: its own current TEC
        features = base_features + [f'tec_{station}']
        target = f'tec_{station}_target_{horizon}'
        
        # Drop rows with NaN in target or features (just in case)
        train_subset = train_df.dropna(subset=features + [target])
        test_subset = test_df.dropna(subset=features + [target])
        
        X_train = train_subset[features]
        y_train = train_subset[target]
        X_test = test_subset[features]
        y_test = test_subset[target]
        
        # Initialize model
        model = xgb.XGBRegressor(
            n_estimators=300, 
            max_depth=6, 
            learning_rate=0.05,
            random_state=42,
            n_jobs=-1
        )
        
        # Train model
        model.fit(X_train, y_train)
        
        # Save model for Stage 5
        model.save_model(f'models/xgb_model_{station}_{horizon}.json')
        
        # Evaluate
        preds = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        mae = mean_absolute_error(y_test, preds)
        r, _ = pearsonr(y_test, preds)
        
        results.append({
            'station': station,
            'horizon': horizon,
            'rmse': rmse,
            'mae': mae,
            'r': r
        })
        
        # Save predictions for stage 5
        test_subset = test_subset.copy()
        test_subset[f'pred_{target}'] = preds
        # We can merge these back later, but for now we just output metrics
        
        print(f"| {station.capitalize()} | {horizon} | {rmse:.4f} | {mae:.4f} | {r:.4f} |")

# Save results for comparison with LSTM later
with open('metrics/stage2_metrics.json', 'w') as f:
    json.dump(results, f)
