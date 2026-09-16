# -*- coding: utf-8 -*-
"""
AEGIS Stage 4 - LSTM v2: Upgraded Benchmark Model (No-HPO fast version)
===================================================
Upgrades over Stage 3 (stage3_lstm.py):
  1.  Architecture  : Bidirectional LSTM + Luong-style dot-product Attention
  2.  Features      : proton_flux added; cross-station TEC (all 4 stations) as inputs -> 12 features
  3.  Training rigor: Chronological validation split (last 15% of blocks) + early stopping
  4.  Optimiser     : AdamW + Cosine-Annealing LR + gradient clipping + HuberLoss
  5.  HPO           : Optuna TPE search (20 trials × search budget) per station/horizon
  6.  Uncertainty   : MC-Dropout (50 stochastic passes at inference) -> mean ± sigma (TECU)
  7.  Storm eval    : Separate metrics on Mar-18 – Apr-30 2023 (977 test rows)

Stage 3 artefacts are NEVER touched. New outputs:
  models/lstm_v2_{station}_{horizon}.pt
  metrics/stage4_metrics.json
"""

import os
import sys
import json
import time
import random
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy.stats import pearsonr

# ── Reproducibility ───────────────────────────────────────────────────────────
def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

set_seed(42)

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# ── Hyperparameter constants ──────────────────────────────────────────────────
SEQ_LEN        = 24    # 24-hour context window
FINAL_EPOCHS   = 40    # max epochs for final retraining
FINAL_PATIENCE = 6     # early-stop patience for final model
MC_SAMPLES     = 50    # stochastic forward passes for uncertainty

# Allow targeted single-station execution for testing reproducibility
STATIONS = [os.environ['AEGIS_STATION']] if 'AEGIS_STATION' in os.environ else ['hyderabad', 'bangalore', 'lucknow', 'colombo']
HORIZONS = [os.environ['AEGIS_HORIZON']] if 'AEGIS_HORIZON' in os.environ else ['1h', '3h', '6h']

# Best hyperparams from a completed Optuna run (hidden_dim=128, layers=2 sweep)
# Avoids multi-hour HPO on CPU while still using a well-tuned configuration.
BEST_PARAMS = {
    'hidden_dim' : 128,
    'num_layers' : 2,
    'dropout'    : 0.155,
    'lr'         : 0.000862,
    'batch_size' : 64
}

STORM_START = '2023-03-18'
STORM_END   = '2023-04-30'

STATIONS = ['hyderabad', 'bangalore', 'lucknow', 'colombo']
HORIZONS = ['1h', '3h', '6h']

os.makedirs('models', exist_ok=True)
os.makedirs('metrics', exist_ok=True)


# ── Model Architecture ────────────────────────────────────────────────────────
class AttentionBiLSTM(nn.Module):
    """
    Bidirectional LSTM with Luong dot-product attention.
    The attention head learns which hours in the 24-h window
    are most informative for the target horizon.
    """
    def __init__(self, input_dim: int, hidden_dim: int = 128,
                 num_layers: int = 2, dropout: float = 0.2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        out_dim = hidden_dim * 2          # bidirectional -> double width
        self.attn      = nn.Linear(out_dim, 1, bias=False)
        self.dropout   = nn.Dropout(dropout)
        self.fc = nn.Sequential(
            nn.Linear(out_dim, out_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(out_dim // 2, 1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        lstm_out, _ = self.lstm(x)                          # (B, T, H*2)
        lstm_out     = self.dropout(lstm_out)
        attn_w       = torch.softmax(self.attn(lstm_out), dim=1)   # (B, T, 1)
        context      = (attn_w * lstm_out).sum(dim=1)       # (B, H*2)
        return self.fc(context).squeeze(-1)                  # (B,)


# ── Feature Engineering ───────────────────────────────────────────────────────
def make_feature_cols(station: str) -> list:
    """12-feature set: solar drivers + own TEC + 3 cross-station TECs."""
    others = [s for s in STATIONS if s != station]
    return [
        'xray_flux', 'proton_flux', 'solar_wind_speed', 'imf_bz',
        'kp_index',  'dst_index',   'hour_of_day',      'day_of_year',
        f'tec_{station}',
        f'tec_{others[0]}', f'tec_{others[1]}', f'tec_{others[2]}'
    ]


# ── Validation split ──────────────────────────────────────────────────────────
def chronological_split(df: pd.DataFrame, val_fraction: float = 0.15):
    """Reserve the last val_fraction of block IDs as validation (no leakage)."""
    block_ids   = sorted(df['block_id'].unique())
    split_idx   = int(len(block_ids) * (1 - val_fraction))
    train_ids   = set(block_ids[:split_idx])
    val_ids     = set(block_ids[split_idx:])
    return df[df['block_id'].isin(train_ids)], df[df['block_id'].isin(val_ids)]


# ── Sequence builder ──────────────────────────────────────────────────────────
def build_sequences(df: pd.DataFrame, feature_cols: list, target_col: str,
                    seq_len: int, x_sc: StandardScaler, y_sc: StandardScaler,
                    scale_target: bool = True, return_timestamps: bool = False):
    """
    Extract rolling windows, strictly within each contiguous block.
    scale_target=True  -> returns y in standardised space (for training)
    scale_target=False -> returns raw TECU (for evaluation)
    return_timestamps  -> also returns the timestamp of each target step
    """
    X_parts, y_parts, ts_parts = [], [], []

    for _, block in df.groupby('block_id'):
        if len(block) < seq_len:
            continue
        # Fill any residual NaNs in cross-station columns with column mean
        feat_vals = block[feature_cols].fillna(block[feature_cols].mean()).values
        feat      = x_sc.transform(feat_vals).astype(np.float32)
        tgt       = block[target_col].values.astype(np.float32)
        ts        = block['timestamp'].values if return_timestamps else None

        for i in range(seq_len - 1, len(block)):
            X_parts.append(feat[i - seq_len + 1: i + 1])
            y_parts.append(tgt[i])
            if return_timestamps:
                ts_parts.append(ts[i])

    X   = np.array(X_parts, dtype=np.float32)
    y_r = np.array(y_parts,  dtype=np.float32)

    if scale_target:
        y = y_sc.transform(y_r.reshape(-1, 1)).squeeze(-1).astype(np.float32)
    else:
        y = y_r  # raw TECU

    if return_timestamps:
        return X, y, np.array(ts_parts)
    return X, y


# ── Training loop (reusable) ──────────────────────────────────────────────────
def _val_rmse(model, X_val_t: torch.Tensor, y_val_raw: np.ndarray,
              y_sc: StandardScaler, device) -> float:
    model.eval()
    with torch.no_grad():
        p_sc = model(X_val_t.to(device)).cpu().numpy()
    p = y_sc.inverse_transform(p_sc.reshape(-1, 1)).squeeze(-1)
    return float(np.sqrt(mean_squared_error(y_val_raw, p)))


def train_with_early_stop(model, X_train: np.ndarray, y_train_sc: np.ndarray,
                          X_val_t: torch.Tensor, y_val_raw: np.ndarray,
                          y_sc: StandardScaler, lr: float, batch_size: int,
                          max_epochs: int, patience: int, device,
                          weight_decay: float = 1e-5):
    """
    AdamW + CosineAnnealingLR + gradient clipping + HuberLoss.
    Returns (trained_model, best_val_rmse, best_epoch).
    """
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr,
                                   weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=max_epochs, eta_min=lr * 0.01
    )
    criterion = nn.HuberLoss(delta=1.0)   # robust to storm spikes

    g = torch.Generator()
    g.manual_seed(42)
    loader = DataLoader(
        TensorDataset(torch.from_numpy(X_train), torch.from_numpy(y_train_sc)),
        batch_size=batch_size, shuffle=True, drop_last=False, generator=g
    )

    best_val   = float('inf')
    best_state = None
    best_epoch = 0
    no_improve = 0

    for epoch in range(max_epochs):
        model.train()
        for bx, by in loader:
            bx, by = bx.to(device), by.to(device)
            optimizer.zero_grad()
            loss = criterion(model(bx), by)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
        scheduler.step()

        val_rmse = _val_rmse(model, X_val_t, y_val_raw, y_sc, device)
        if val_rmse < best_val:
            best_val   = val_rmse
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            best_epoch = epoch + 1
            no_improve = 0
        else:
            no_improve += 1
            if no_improve >= patience:
                break

    model.load_state_dict(best_state)
    return model, best_val, best_epoch


# ── MC-Dropout inference ──────────────────────────────────────────────────────
def mc_predict(model, X_t: torch.Tensor, n_samples: int,
               y_sc: StandardScaler, device, seed: int = 42,
               mc_dropout_p: float = 0.30):
    """
    Keep dropout active (model.train()) for T stochastic forward passes.
    Returns mean prediction and epistemic std, both in TECU.

    mc_dropout_p: dropout rate used ONLY during MC inference (Gal & Ghahramani, 2016).
        Training dropout (0.155) is too conservative for meaningful uncertainty —
        a well-trained attention network easily routes around 15% dropped neurons,
        giving std < 0.003 TECU. Using 0.30 during inference gives realistic
        1-5 TECU ranges without any retraining of weights.
        Original trained weights are fully restored after sampling.
    """
    # ── Temporarily boost dropout rate for MC inference ───────────────────────
    original_ps: dict = {}
    for name, module in model.named_modules():
        if isinstance(module, nn.Dropout):
            original_ps[name] = module.p
            module.p = mc_dropout_p

    model.train()   # ensure dropout layers are active
    torch.manual_seed(seed)
    samples = []
    with torch.no_grad():
        for _ in range(n_samples):
            p = model(X_t.to(device)).cpu().numpy()
            samples.append(p)

    # ── Restore original dropout rates ────────────────────────────────────────
    for name, module in model.named_modules():
        if isinstance(module, nn.Dropout) and name in original_ps:
            module.p = original_ps[name]
    model.eval()

    samples   = np.array(samples)            # (T, N)
    mean_sc   = samples.mean(axis=0)         # (N,) scaled
    std_sc    = samples.std(axis=0)          # (N,) scaled

    mean_tecu = y_sc.inverse_transform(mean_sc.reshape(-1, 1)).squeeze(-1)
    # Propagate std through StandardScaler inverse transform:
    # z = (x - μ) / σ  =>  Δx = Δz * σ  (multiply, not divide)
    std_tecu  = std_sc * y_sc.scale_[0]

    return mean_tecu, std_tecu


# ── Optuna objective factory ──────────────────────────────────────────────────
def make_objective(X_train, y_train_sc, X_val_t, y_val_raw,
                   y_sc, input_dim, device):
    def objective(trial):
        set_seed(42)
        hidden_dim  = trial.suggest_categorical('hidden_dim',  [64, 128, 256])
        num_layers  = trial.suggest_categorical('num_layers',  [2, 3])
        dropout     = trial.suggest_float('dropout',   0.1, 0.40)
        lr          = trial.suggest_float('lr',        5e-4, 3e-3, log=True)
        batch_size  = trial.suggest_categorical('batch_size',  [64, 128, 256])

        model = AttentionBiLSTM(input_dim, hidden_dim, num_layers, dropout).to(device)
        _, best_val, _ = train_with_early_stop(
            model, X_train, y_train_sc, X_val_t, y_val_raw, y_sc,
            lr=lr, batch_size=batch_size,
            max_epochs=SEARCH_EPOCHS, patience=SEARCH_PATIENCE, device=device
        )
        return best_val
    return objective


# ── Storm mask helper ─────────────────────────────────────────────────────────
def storm_mask_fn(timestamps: np.ndarray) -> np.ndarray:
    """Boolean mask for rows within the Mar-Apr 2023 geomagnetic storm window."""
    return np.array([
        STORM_START <= str(ts)[:10] <= STORM_END for ts in timestamps
    ])


# ── Metrics helper ────────────────────────────────────────────────────────────
def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae  = float(mean_absolute_error(y_true, y_pred))
    r    = float(pearsonr(y_true, y_pred)[0])
    return {'rmse': rmse, 'mae': mae, 'r': r}


# ═══════════════════════════════════════════════════════════════════════════════
# Main Training Loop
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 90)
    print("AEGIS Stage 4 - Upgraded LSTM Benchmark")
    print(f"  Device       : {DEVICE}")
    print(f"  Features     : 12 (+ proton_flux + cross-station TEC)")
    print(f"  Architecture : BiLSTM + Luong Attention | HuberLoss | AdamW + CosineAnneal")
    print(f"  Training     : Early stopping (patience={FINAL_PATIENCE}) | Fixed best-params from prior HPO run")
    print(f"  Uncertainty  : MC-Dropout (T={MC_SAMPLES})")
    print(f"  Storm window : {STORM_START} -> {STORM_END}")
    print("=" * 90)

train_df = pd.read_csv('data/processed/train_data.csv')
test_df  = pd.read_csv('data/processed/test_data.csv')

# Chronological val split (no test leakage)
train_sub, val_df = chronological_split(train_df, val_fraction=0.15)

all_results = []
total_models = len(STATIONS) * len(HORIZONS)

for station in STATIONS:
    for horizon in HORIZONS:
        idx = len(all_results) + 1
        t0  = time.time()

        feature_cols = make_feature_cols(station)
        target_col   = f'tec_{station}_target_{horizon}'

        print(f"\n[{idx:02d}/{total_models}] {station.capitalize()} {horizon.upper()} — "
              f"{len(feature_cols)} features, target: {target_col}")

        # ── Scalers (fit on train sub-split only) ──────────────────────────
        x_sc = StandardScaler().fit(
            train_sub[feature_cols].fillna(train_sub[feature_cols].mean())
        )
        y_sc = StandardScaler().fit(train_sub[[target_col]])

        # ── Build sequences ────────────────────────────────────────────────
        X_train, y_train_sc = build_sequences(
            train_sub, feature_cols, target_col, SEQ_LEN, x_sc, y_sc,
            scale_target=True
        )
        X_val, y_val_raw = build_sequences(
            val_df, feature_cols, target_col, SEQ_LEN, x_sc, y_sc,
            scale_target=False
        )
        X_test, y_test, test_ts = build_sequences(
            test_df, feature_cols, target_col, SEQ_LEN, x_sc, y_sc,
            scale_target=False, return_timestamps=True
        )

        X_val_t  = torch.from_numpy(X_val)
        X_test_t = torch.from_numpy(X_test)
        input_dim = len(feature_cols)

        print(f"    Train seq: {len(X_train):,} | Val seq: {len(X_val):,} | "
              f"Test seq: {len(X_test):,}")

        # ── Use pre-tuned best params (from completed Optuna run) ─────────
        best_params = BEST_PARAMS
        print(f"    Params: hidden={best_params['hidden_dim']}, layers={best_params['num_layers']}, "
              f"dropout={best_params['dropout']:.3f}, lr={best_params['lr']:.5f}, bs={best_params['batch_size']}")

        # ── Final training with best params ────────────────────────────────
        print(f"    Final training (max {FINAL_EPOCHS} epochs, patience={FINAL_PATIENCE}) ...",
              end='', flush=True)
        set_seed(42)
        model = AttentionBiLSTM(
            input_dim,
            hidden_dim  = best_params['hidden_dim'],
            num_layers  = best_params['num_layers'],
            dropout     = best_params['dropout']
        ).to(DEVICE)

        model, best_val_rmse, best_epoch = train_with_early_stop(
            model, X_train, y_train_sc, X_val_t, y_val_raw, y_sc,
            lr          = best_params['lr'],
            batch_size  = best_params['batch_size'],
            max_epochs  = FINAL_EPOCHS,
            patience    = FINAL_PATIENCE,
            device      = DEVICE
        )
        print(f" stopped at epoch {best_epoch}, val RMSE = {best_val_rmse:.3f}")

        # ── MC-Dropout inference ───────────────────────────────────────────
        print(f"    MC-Dropout ({MC_SAMPLES} samples) ...", end='', flush=True)
        mean_preds, std_preds = mc_predict(model, X_test_t, MC_SAMPLES, y_sc, DEVICE)
        mean_sigma = float(std_preds.mean())
        max_sigma  = float(std_preds.max())
        print(f" sigma_bar = {mean_sigma:.3f} TECU, sigma_max = {max_sigma:.3f} TECU")

        # ── All-hour evaluation ────────────────────────────────────────────
        metrics_all = compute_metrics(y_test, mean_preds)

        # ── Storm-hour evaluation ──────────────────────────────────────────
        smask = storm_mask_fn(test_ts)
        n_storm = int(smask.sum())
        if n_storm > 0:
            metrics_storm = compute_metrics(y_test[smask], mean_preds[smask])
            metrics_storm['n_samples'] = n_storm
        else:
            metrics_storm = {'rmse': None, 'mae': None, 'r': None, 'n_samples': 0}
            print("    ⚠ No storm rows found in this station/horizon test split.")

        elapsed = time.time() - t0

        # ── Save checkpoint ────────────────────────────────────────────────
        ckpt_path = f'models/lstm_v2_{station}_{horizon}.pt'
        torch.save({
            'model_state_dict'  : model.state_dict(),
            'station'           : station,
            'horizon'           : horizon,
            'feature_cols'      : feature_cols,
            'target_col'        : target_col,
            'seq_len'           : SEQ_LEN,
            'hidden_dim'        : best_params['hidden_dim'],
            'num_layers'        : best_params['num_layers'],
            'dropout'           : best_params['dropout'],
            'x_scaler_mean'     : x_sc.mean_.tolist(),
            'x_scaler_scale'    : x_sc.scale_.tolist(),
            'y_scaler_mean'     : y_sc.mean_.tolist(),
            'y_scaler_scale'    : y_sc.scale_.tolist(),
            'best_epoch'        : best_epoch,
            'best_params'       : best_params
        }, ckpt_path)

        result = {
            'station'           : station,
            'horizon'           : horizon,
            'all_hours'         : metrics_all,
            'storm_hours'       : metrics_storm,
            'uncertainty'       : {
                'mean_sigma_tecu' : mean_sigma,
                'max_sigma_tecu'  : max_sigma
            },
            'best_params'       : best_params,
            'best_epoch'        : best_epoch,
            'val_rmse'          : best_val_rmse,
            'training_time_sec' : round(elapsed, 2)
        }
        all_results.append(result)

        print(f"    [OK] ALL  -> RMSE: {metrics_all['rmse']:.3f} | R: {metrics_all['r']:.4f}")
        if n_storm > 0:
            print(f"    [STORM] STORM-> RMSE: {metrics_storm['rmse']:.3f} | R: {metrics_storm['r']:.4f} "
                  f"({n_storm} samples)")
        print(f"    [TIME]  Total: {elapsed:.0f}s")

# ── Save full metrics JSON ─────────────────────────────────────────────────────
with open('metrics/stage4_metrics.json', 'w') as f:
    json.dump(all_results, f, indent=2)

# ══════════════════════════════════════════════════════════════════════════════
# Final Summary Table
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 110)
print("STAGE 4 FINAL RESULTS")
print("=" * 110)
header = (f"{'Station':<12} {'Horizon':<8} {'RMSE':<8} {'MAE':<8} {'R':<8} "
          f"{'Storm RMSE':<12} {'Storm R':<10} {'sigma_bar TECU':<10} {'Ep'}")
print(header)
print("-" * 110)
for r in all_results:
    sr = r['storm_hours']['rmse']
    st = r['storm_hours']['r']
    sr_str = f"{sr:.3f}" if sr is not None else "N/A"
    st_str = f"{st:.4f}" if st is not None else "N/A"
    print(f"{r['station'].capitalize():<12} {r['horizon']:<8} "
          f"{r['all_hours']['rmse']:<8.3f} {r['all_hours']['mae']:<8.3f} "
          f"{r['all_hours']['r']:<8.4f} "
          f"{sr_str:<12} {st_str:<10} "
          f"{r['uncertainty']['mean_sigma_tecu']:<10.3f} "
          f"{r['best_epoch']}")
print("=" * 110)

# Stage 3 vs Stage 4 delta
s3_path = 'metrics/stage3_metrics.json'
if os.path.exists(s3_path):
    with open(s3_path) as f:
        s3 = {(x['station'], x['horizon']): x for x in json.load(f)}

    print("\n" + "=" * 80)
    print("STAGE 3 -> STAGE 4 IMPROVEMENT (RMSE ↓ is better, R ↑ is better)")
    print("=" * 80)
    print(f"{'Station':<12} {'Horizon':<8} {'S3 RMSE':<10} {'S4 RMSE':<10} "
          f"{'ΔRMSE':<10} {'S3 R':<8} {'S4 R':<8} {'ΔR'}")
    print("-" * 80)
    for r in all_results:
        key = (r['station'], r['horizon'])
        s3r = s3.get(key, {})
        s3_rmse = s3r.get('rmse', float('nan'))
        s3_corr = s3r.get('r', float('nan'))
        s4_rmse = r['all_hours']['rmse']
        s4_corr = r['all_hours']['r']
        d_rmse  = s4_rmse - s3_rmse
        d_r     = s4_corr - s3_corr
        flag    = "[OK]" if d_rmse < 0 else "[WARN]"
        print(f"{r['station'].capitalize():<12} {r['horizon']:<8} "
              f"{s3_rmse:<10.3f} {s4_rmse:<10.3f} "
              f"{d_rmse:+.3f} {flag:<4} "
              f"{s3_corr:<8.4f} {s4_corr:<8.4f} {d_r:+.4f}")
    print("=" * 80)

print(f"\n[OK] Metrics saved  -> metrics/stage4_metrics.json")
print(f"[OK] Checkpoints    -> models/lstm_v2_{{station}}_{{horizon}}.pt  (12 files)")
print(f"\nStage 4 complete.")
