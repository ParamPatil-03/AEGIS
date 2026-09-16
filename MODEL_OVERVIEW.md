# AEGIS Model Overview
### Technical Architecture & Operational Guide

---

## 1. What the Model Does

AEGIS is an **ionospheric Total Electron Content (TEC) forecasting model**.  
It predicts ionospheric plasma delay (in **TECU**) to provide early warnings for **GPS positioning errors** and **satellite communication scintillation**.

- **4 GPS Stations:** Colombo, Bangalore, Hyderabad, Lucknow
- **3 Forecast Horizons:** 1 Hour, 3 Hours, 6 Hours ahead
- **Total Operational Models:** $4 \times 3 =$ **12 trained models**

---



`

### Vertical Stage Breakdown

1. **Input Sequence (24h Window):**
   Continuous 24-hour sliding window of solar drivers, geomagnetic indices, and cross-station TEC.
2. **Layer 1 — AttentionBiLSTM (Base Model):**
   Captures diurnal and seasonal trends, applying attention over past hours to generate base forecast $\hat{y}_{\text{lstm}}$.
3. **Layer 2 — XGBoost Residual Stacker (Physics Corrector):**
   Estimates residual error $\hat{e}_{\text{xgb}} = y - \hat{y}_{\text{lstm}}$ using physical electrodynamic features and fountain delays.
4. **Combined Forecast:**
   $$\hat{y}_{\text{final}} = \hat{y}_{\text{lstm}} + \hat{e}_{\text{xgb}}$$
5. **Layer 3 — Adaptive Conformal Safety Interval:**
   Wraps prediction in a certified 95% confidence interval that widens dynamically during storms.

---

## 3. Model Architecture Details

### Layer 1: `AttentionBiLSTM` (Base Model)
- **Bidirectional LSTM:** 2 stacked layers, 128 hidden units per direction ($2 \times 128 = 256$ dimensions).
- **Luong Attention:** Dynamically scores which of the past 24 hours carry the strongest signal for the target forecast step.
- **Huber Loss ($\delta = 1.0$):** Replaces MSE to prevent violent solar flare spikes from destabilizing model weights.
- **Optimization:** AdamW optimizer (`lr = 8.62e-4`), Cosine Annealing learning rate schedule, gradient clipping (`max_norm = 1.0`), and early stopping.
- **Epistemic Uncertainty:** 50 Monte Carlo Dropout forward passes at inference with boosted dropout ($p=0.30$) to output prediction confidence ($\mu \pm \sigma$).

### Layer 2: `XGBoost Residual Stacker` (Physics Corrector)
- **Role:** Corrects systematic biases and extreme storm deviations left by the neural network.
- **Architecture:** 300 gradient-boosted trees, max depth 6, learning rate 0.035, subsample 0.85.
- **Storm-Weighted Training:** Applies up to **15× sample weight** during active storm conditions ($Kp \ge 4.5$ or $Dst \le -40\text{ nT}$), forcing the model to learn rare storm crests.

### Layer 3: Adaptive Conformal Prediction (Safety Bound)
- **Role:** Guarantees true 95% coverage under all conditions.
- **Dynamic Scale Factor:**
  $$s(Kp, Dst) = 1.0 + 0.35 \cdot \max(0, Kp - 3.0) + 0.015 \cdot \max(0, -Dst - 25.0)$$
- **Interval Width:** $\text{Margin} = \pm\,\hat{q}_{\text{adaptive}} \cdot s(Kp, Dst)$
  - **Calm Conditions:** Tight bounds ($\pm 11$ to $18$ TECU).
  - **Severe Solar Storms:** Expands automatically ($\pm 35$ to $96$ TECU), preventing dangerous interval breaches.

---

## 4. Input Features

### Layer 1: AttentionBiLSTM Features (12 Features)
- `xray_flux` — Solar X-ray radiation flux
- `proton_flux` — Solar proton particle flux
- `solar_wind_speed` — Bulk solar wind velocity ($V_{\text{sw}}$)
- `imf_bz` — Interplanetary Magnetic Field $B_z$ component
- `kp_index` — Planetary geomagnetic disturbance index
- `dst_index` — Disturbance Storm Time ring current index
- `hour_of_day` — Local diurnal time cycle
- `day_of_year` — Annual seasonal cycle
- `tec_{station}` — Target station's own historical TEC
- `tec_{cross_1, 2, 3}` — Regional cross-station TEC from all 3 other stations

### Layer 2: XGBoost Residual Features (25 Features)
- **Base Predictions:** $\hat{y}_{\text{lstm}}$, Predicted Delta $(\hat{y}_{\text{lstm}} - \text{current station TEC})$
- **Cyclic Harmonics:** $\sin/\cos(2\pi\cdot\text{hour}/24)$, $\sin/\cos(2\pi\cdot\text{day}/365.25)$
- **Interplanetary E-Field:** $E_y = -V_{\text{sw}} \cdot B_z \cdot 10^{-3}\text{ mV/m}$
- **Equatorial Anomaly (EIA):** Colombo–Station TEC gradient
- **EIA Fountain Transit Lags:** 2-hour and 4-hour lagged EIA gradients (models plasma flow delay from equator to crest)
- **Storm Buildup Derivative:** 3-hour $Dst$ drop rate $d(Dst)/dt$
- **Ionospheric Velocity:** 1h and 3h TEC trend slopes for station and Colombo
- **Space Weather Telemetry:** $V_{\text{sw}}$, $B_z$, $Kp$, $Dst$, X-ray flux, Proton flux
- **Regional Snapshot:** Current TEC across all 4 stations

---

## 5. Robustness Improvements Implemented

1. **Storm Conformal Deficit Eliminated:**
   - *Previous issue:* Fixed intervals suffered an empirical breach rate of up to 36.6% during storms.
   - *Fix:* Replaced fixed quantile with dynamic scaling $s(Kp, Dst)$.
   - *Result:* Storm coverage is now **$\ge 95.7\%$ across all 12 models**.
2. **Lucknow 6h Storm Underestimation Fixed:**
   - *Previous issue:* Plasma fountain travel delay caused errors exceeding 100 TECU during storm peaks.
   - *Fix:* Added 2h/4h lagged EIA gradients and storm sample weighting up to 15×.
   - *Result:* Lucknow 6h RMSE dropped from 17.26 to **15.79 TECU** ($\Delta = -1.47$ TECU); 3h RMSE dropped from 13.95 to **12.27 TECU**.
3. **Epistemic Uncertainty Calibrated:**
   - Boosted inference MC-Dropout probability to $p=0.30$ for 50 passes, producing realistic $\pm 1$ to $5$ TECU uncertainty bars.

---

## 6. Official Verified Performance Benchmark

*Evaluated on independent test data, including the March 2023 G4 geomagnetic storm:*

| Station | Horizon | Stage 4 RMSE | Stage 5 RMSE | Correlation ($R$) | Storm Cov. ($Kp \ge 5$) | Status |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Hyderabad** | 1h | 7.33 | **7.07** | **0.9863** | **100.0%** | **PASS** |
| **Hyderabad** | 3h | 11.16 | **11.04** | **0.9668** | **100.0%** | **PASS** |
| **Hyderabad** | 6h | 14.08 | **13.23** | **0.9519** | **95.7%** | **PASS** |
| **Bangalore** | 1h | 6.38 | **6.14** | **0.9882** | **100.0%** | **PASS** |
| **Bangalore** | 3h | 9.28 | **8.92** | **0.9747** | **100.0%** | **PASS** |
| **Bangalore** | 6h | 9.63 | **9.33** | **0.9723** | **100.0%** | **PASS** |
| **Lucknow** | 1h | 9.68 | **9.01** | **0.9778** | **97.8%** | **PASS** |
| **Lucknow** | 3h | 13.95 | **12.27** | **0.9583** | **100.0%** | **PASS** |
| **Lucknow** | 6h | 17.26 | **15.79** | **0.9304** | **100.0%** | **PASS** |
| **Colombo** | 1h | 6.71 | **6.39** | **0.9878** | **100.0%** | **PASS** |
| **Colombo** | 3h | 9.38 | **9.19** | **0.9764** | **97.8%** | **PASS** |
| **Colombo** | 6h | 11.06 | **10.64** | **0.9673** | **100.0%** | **PASS** |

---

## 7. Hyperparameter Quick Sheet

- **Lookback Window:** 24 hours
- **BiLSTM Dimension:** 2 layers $\times$ 128 units (256 bidirectional)
- **Training Dropout:** 0.155 (Training) | **Inference Dropout:** 0.30 (MC passes: 50)
- **Learning Rate:** $8.62 \times 10^{-4}$ (AdamW + CosineAnnealingLR)
- **Loss:** HuberLoss ($\delta = 1.0$)
- **XGBoost Regressor:** 300 estimators, max depth 6, learning rate 0.035
- **Storm Weight Formula:**
  $$w = 1.0 + 4.0 \cdot \left(\frac{\max(0, Kp - 3)}{3}\right)^2 + 2.0 \cdot \left(\frac{\max(0, -Dst - 30)}{50}\right)$$
