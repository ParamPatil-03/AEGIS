import pandas as pd
import numpy as np

# Load data
solar = pd.read_csv('data/raw/solar_data.csv')
tec = pd.read_csv('data/raw/tec_data.csv')

# Ensure timestamp is datetime
solar['timestamp'] = pd.to_datetime(solar['timestamp'])
tec['timestamp'] = pd.to_datetime(tec['timestamp'])

# Merge data
df = pd.merge(solar, tec, on='timestamp', how='inner')
df = df.sort_values('timestamp').reset_index(drop=True)

# Keep only rows where all 4 stations have valid data
tec_stations = ['tec_hyderabad', 'tec_bangalore', 'tec_lucknow', 'tec_colombo']
df = df.dropna(subset=tec_stations).copy()

print(f"Row count before lag/target processing: {len(df)}")

# Identify continuous stretches of time
df['diff'] = df['timestamp'].diff()
# A new group starts whenever the difference is not exactly 1 hour
df['group'] = (df['diff'] != pd.Timedelta(hours=1)).cumsum()

# Define features
solar_features = ['xray_flux', 'solar_wind_speed', 'imf_bz', 'kp_index', 'dst_index']
lags = [1, 3, 6, 12, 24]
leads = [1, 3, 6]

new_cols = []

# Add lags (within continuous groups)
for feat in solar_features:
    for lag in lags:
        col_name = f'{feat}_lag_{lag}h'
        df[col_name] = df.groupby('group')[feat].shift(lag)
        new_cols.append(col_name)

# Add leads (targets, within continuous groups)
for stat in tec_stations:
    for lead in leads:
        col_name = f'{stat}_target_{lead}h'
        df[col_name] = df.groupby('group')[stat].shift(-lead)
        new_cols.append(col_name)

# Add time features
df['hour_of_day'] = df['timestamp'].dt.hour
df['day_of_year'] = df['timestamp'].dt.dayofyear

# Drop rows with NaN in required lag or target columns (edge rows of the groups)
df_final = df.dropna(subset=new_cols).copy()

# Drop the temporary grouping columns
df_final = df_final.drop(columns=['diff', 'group'])

# Save to CSV
df_final.to_csv('data/processed/model_ready_data.csv', index=False)

# Print results
print("\n--- Summary ---")
print(f"Final row count after dropping edge rows: {len(df_final)}")
print("\nRemaining nulls in all columns:")
null_counts = df_final.isnull().sum()
print(null_counts[null_counts > 0])
