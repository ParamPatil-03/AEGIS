import os
import json
import time
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy.stats import pearsonr

# Set random seeds for reproducibility
def set_seed(seed=42):
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

set_seed(42)

# Ensure output directories exist
os.makedirs('models', exist_ok=True)
os.makedirs('metrics', exist_ok=True)

# Load Stage 1 split datasets
train_df = pd.read_csv('data/processed/train_data.csv')
test_df = pd.read_csv('data/processed/test_data.csv')

stations = ['hyderabad', 'bangalore', 'lucknow', 'colombo']
horizons = ['1h', '3h', '6h']

# Sequence length: 24 hourly steps gives a full 24-hour diurnal/solar cycle context
SEQ_LEN = 24
EPOCHS = 20
BATCH_SIZE = 128
LEARNING_RATE = 0.001
WEIGHT_DECAY = 1e-5
HIDDEN_DIM = 64
NUM_LAYERS = 2
DROPOUT = 0.2

# Define PyTorch LSTM Regressor Architecture
class LSTMRegressor(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, num_layers=2, dropout=0.2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )
        
    def forward(self, x):
        out, _ = self.lstm(x)
        last_step = out[:, -1, :]
        return self.fc(last_step).squeeze(-1)

# Sequence extraction respecting block boundaries (strictly avoiding leakage or gap-crossing)
def create_block_sequences(df, feature_cols, target_col, seq_len=24, x_scaler=None, y_scaler=None, is_train=True):
    X_list = []
    y_list = []
    
    if is_train:
        x_scaler = StandardScaler()
        x_scaler.fit(df[feature_cols])
        y_scaler = StandardScaler()
        y_scaler.fit(df[[target_col]])
        
    for block_id, block in df.groupby('block_id'):
        if len(block) < seq_len:
            continue
        # Standardize features using the train scaler
        feat_arr = x_scaler.transform(block[feature_cols])
        target_arr = block[target_col].values
        
        # Build rolling windows strictly within each contiguous block
        for i in range(seq_len - 1, len(block)):
            X_list.append(feat_arr[i - seq_len + 1 : i + 1])
            y_list.append(target_arr[i])
            
    X_arr = np.array(X_list, dtype=np.float32)
    y_raw = np.array(y_list, dtype=np.float32)
    
    if is_train:
        y_scaled = y_scaler.transform(y_raw.reshape(-1, 1)).squeeze(-1).astype(np.float32)
        return X_arr, y_scaled, x_scaler, y_scaler
    else:
        return X_arr, y_raw, x_scaler, y_scaler

# Load existing Stage 2 XGBoost metrics for direct side-by-side comparison
stage2_metrics = {}
if os.path.exists('metrics/stage2_metrics.json'):
    with open('metrics/stage2_metrics.json', 'r') as f:
        stage2_list = json.load(f)
        for item in stage2_list:
            key = (item['station'].lower(), item['horizon'].lower())
            stage2_metrics[key] = item

lstm_results = []

print("=" * 70)
print("Starting Stage 3: LSTM Benchmark Model Training (12 models)")
print(f"Sequence length: {SEQ_LEN}h | Epochs: {EPOCHS} | Batch size: {BATCH_SIZE} | Hidden: {HIDDEN_DIM}x{NUM_LAYERS}")
print("=" * 70)

for station in stations:
    for horizon in horizons:
        t0 = time.time()
        
        # Define step features for the station
        step_features = [
            'xray_flux', 'solar_wind_speed', 'imf_bz', 'kp_index', 'dst_index',
            'hour_of_day', 'day_of_year', f'tec_{station}'
        ]
        target = f'tec_{station}_target_{horizon}'
        
        # Prepare sequence datasets
        X_train, y_train, x_scaler, y_scaler = create_block_sequences(
            train_df, step_features, target, seq_len=SEQ_LEN, is_train=True
        )
        X_test, y_test, _, _ = create_block_sequences(
            test_df, step_features, target, seq_len=SEQ_LEN, x_scaler=x_scaler, y_scaler=y_scaler, is_train=False
        )
        
        # Instantiate model
        set_seed(42)
        model = LSTMRegressor(
            input_dim=len(step_features),
            hidden_dim=HIDDEN_DIM,
            num_layers=NUM_LAYERS,
            dropout=DROPOUT
        )
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
        
        train_dataset = TensorDataset(torch.from_numpy(X_train), torch.from_numpy(y_train))
        train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
        
        # Train LSTM
        model.train()
        for epoch in range(EPOCHS):
            for bx, by in train_loader:
                optimizer.zero_grad()
                preds = model(bx)
                loss = criterion(preds, by)
                loss.backward()
                optimizer.step()
                
        # Evaluate on test set
        model.eval()
        with torch.no_grad():
            test_preds_scaled = model(torch.from_numpy(X_test)).numpy()
            test_preds = y_scaler.inverse_transform(test_preds_scaled.reshape(-1, 1)).squeeze(-1)
            
        rmse = float(np.sqrt(mean_squared_error(y_test, test_preds)))
        mae = float(mean_absolute_error(y_test, test_preds))
        r, _ = pearsonr(y_test, test_preds)
        r = float(r)
        
        elapsed = time.time() - t0
        
        # Save model checkpoint and scalers
        checkpoint_path = f'models/lstm_model_{station}_{horizon}.pt'
        torch.save({
            'model_state_dict': model.state_dict(),
            'station': station,
            'horizon': horizon,
            'step_features': step_features,
            'target': target,
            'seq_len': SEQ_LEN,
            'hidden_dim': HIDDEN_DIM,
            'num_layers': NUM_LAYERS,
            'dropout': DROPOUT,
            'x_scaler_mean': x_scaler.mean_.tolist(),
            'x_scaler_scale': x_scaler.scale_.tolist(),
            'y_scaler_mean': y_scaler.mean_.tolist(),
            'y_scaler_scale': y_scaler.scale_.tolist()
        }, checkpoint_path)
        
        res = {
            'station': station,
            'horizon': horizon,
            'rmse': rmse,
            'mae': mae,
            'r': r,
            'training_time_sec': round(elapsed, 2)
        }
        lstm_results.append(res)
        
        print(f"[{len(lstm_results):02d}/12] Completed {station.capitalize()} {horizon.upper()} in {elapsed:.1f}s | RMSE: {rmse:.4f} | MAE: {mae:.4f} | R: {r:.4f}")

# Save metrics to JSON
with open('metrics/stage3_metrics.json', 'w') as f:
    json.dump(lstm_results, f, indent=2)

print("\n" + "=" * 70)
print("STAGE 3 LSTM BENCHMARK RESULTS")
print("=" * 70)
print("| Station | Horizon | RMSE | MAE | R |")
print("|---------|---------|------|-----|---|")
for res in lstm_results:
    print(f"| {res['station'].capitalize():<9} | {res['horizon']:<7} | {res['rmse']:<6.4f} | {res['mae']:<5.4f} | {res['r']:<5.4f} |")

print("\n" + "=" * 90)
print("SIDE-BY-SIDE COMPARISON: XGBOOST (STAGE 2) vs LSTM (STAGE 3)")
print("=" * 90)
print("| Station | Horizon | XGB RMSE | LSTM RMSE | XGB MAE | LSTM MAE | XGB R | LSTM R | Winner (RMSE) |")
print("|---------|---------|----------|-----------|---------|----------|-------|--------|---------------|")

for res in lstm_results:
    key = (res['station'].lower(), res['horizon'].lower())
    xgb_res = stage2_metrics.get(key, {'rmse': float('nan'), 'mae': float('nan'), 'r': float('nan')})
    
    xgb_rmse = xgb_res['rmse']
    lstm_rmse = res['rmse']
    xgb_mae = xgb_res['mae']
    lstm_mae = res['mae']
    xgb_r = xgb_res['r']
    lstm_r = res['r']
    
    diff_rmse = lstm_rmse - xgb_rmse
    pct_rmse = (abs(diff_rmse) / xgb_rmse) * 100
    
    if lstm_rmse < xgb_rmse:
        winner = f"LSTM (-{pct_rmse:.1f}%)"
    else:
        winner = f"XGBoost (+{pct_rmse:.1f}%)"
        
    print(f"| {res['station'].capitalize():<9} | {res['horizon']:<7} | {xgb_rmse:<8.4f} | {lstm_rmse:<9.4f} | {xgb_mae:<7.4f} | {lstm_mae:<8.4f} | {xgb_r:<5.4f} | {lstm_r:<6.4f} | {winner:<13} |")
print("=" * 90)
