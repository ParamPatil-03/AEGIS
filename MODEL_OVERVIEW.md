# AEGIS Model Overview
### Technical Architecture, Data Provenance & Operational Diagnostic Audit

---

## 1. What the Model Does

AEGIS is an **ionospheric Total Electron Content (TEC) forecasting model**.  
It predicts ionospheric plasma delay (in **TECU**, where $1\text{ TECU} = 10^{16}\text{ electrons/m}^2$) to provide early warnings for **GPS/NavIC positioning errors** and **trans-ionospheric radio scintillation**.

- **4 Monitored Stations:** Colombo (Sri Lanka; EIA proxy), Bangalore, Hyderabad, Lucknow
- **3 Forecast Horizons:** 1 Hour, 3 Hours, 6 Hours ahead
- **Total Operational Models:** $4 \times 3 =$ **12 trained models**

---

## 2. Data Provenance & Station Selection

### Station Network & Geographic Distribution
- **Colombo (SGOC, Sri Lanka — $6.89^\circ\text{N}, 79.87^\circ\text{E}$):** Located near the geomagnetic equator ($0.2^\circ\text{N}$ magnetic latitude). **Colombo is a Sri Lankan station used strictly as an equatorial baseline proxy** to observe the source of the Equatorial Fountain effect. It is **NOT** an Indian station.
- **Bangalore (IISC, India — $13.02^\circ\text{N}, 77.57^\circ\text{E}$):** Sub-equatorial transitional zone.
- **Hyderabad (HYDE, India — $17.42^\circ\text{N}, 78.55^\circ\text{E}$):** Southern flank of the northern EIA crest.
- **Lucknow (LCK4, India — $26.91^\circ\text{N}, 80.96^\circ\text{E}$):** Northern EIA crest anomaly peak.

### Omitted Stations
- **Delhi and Trivandrum:** Originally planned in the network design, but dropped from the study because NASA CDDIS archived no continuous, usable RINEX observation files for either station across the 2020–2024 period.

### Data Cleaning & Imputation Audit (`impute_tec.py`)
Data was acquired at hourly resolution over 5 full years (2020-01-01 to 2024-12-31, totaling **43,848 hours**).
1. **Outlier Removal:** Values below $-50\text{ TECU}$ (unphysical GPS receiver lock losses) are replaced with `NaN`.
2. **Linear Interpolation:** Applied **strictly to short gaps of $\le 6$ consecutive hours**.
3. **Longer Gaps ($> 6$ hours):** Left as `NaN` and segmented into disjoint sequence blocks during training.

| Station | Total Hours | Observed Hours | Interpolated ($\le 6$h) | Unresolved Gaps ($> 6$h) | Imputation Fraction |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Hyderabad (HYDE)** | 43,848 | 33,715 (76.9%) | 378 (0.9%) | 9,755 (22.2%) | **0.9%** |
| **Bangalore (IISC)** | 43,848 | 40,806 (93.1%) | 101 (0.2%) | 2,941 (6.7%) | **0.2%** |
| **Lucknow (LCK4)** | 43,848 | 36,964 (84.3%) | 385 (0.9%) | 6,499 (14.8%) | **0.9%** |
| **Colombo (SGOC)** | 43,848 | 41,453 (94.5%) | 146 (0.3%) | 2,249 (5.1%) | **0.3%** |

> [!WARNING]
> **Imputed Values Are Not Ground Truth:** Linearly interpolated values represent synthetic continuity approximations. They smooth out short-term physical ionospheric turbulence and do not reflect observed physical measurements.

---

## 3. Verified Performance Benchmark & Known Limitations

### Verified Test Benchmark (Stage 6 Audit)
The following table reflects actual measured values on the independent test set (2023–2024, 3,867 test hours including the March 2023 G4 geomagnetic storm).

| Station | Horizon | Stage 4 LSTM RMSE | Stage 5 Ensemble RMSE | Correlation ($R$) | Global Storm Coverage ($Kp \ge 5$) | Storm Conformal Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Hyderabad** | 1h | 7.30 | **7.07** | **0.9863** | **81.7%** | <span style="color:red">**FAIL (< 95%)**</span> |
| **Hyderabad** | 3h | 11.18 | **11.04** | **0.9668** | **76.3%** | <span style="color:red">**FAIL (< 95%)**</span> |
| **Hyderabad** | 6h | 14.08 | **13.23** | **0.9519** | **68.8%** | <span style="color:red">**FAIL (< 95%)**</span> |
| **Bangalore** | 1h | 6.35 | **6.14** | **0.9882** | **87.1%** | <span style="color:red">**FAIL (< 95%)**</span> |
| **Bangalore** | 3h | 9.28 | **8.92** | **0.9747** | **81.7%** | <span style="color:red">**FAIL (< 95%)**</span> |
| **Bangalore** | 6h | 9.61 | **9.33** | **0.9723** | **74.2%** | <span style="color:red">**FAIL (< 95%)**</span> |
| **Lucknow** | 1h | 9.61 | **9.01** | **0.9778** | **86.0%** | <span style="color:red">**FAIL (< 95%)**</span> |
| **Lucknow** | 3h | 13.88 | **12.27** | **0.9583** | **83.9%** | <span style="color:red">**FAIL (< 95%)**</span> |
| **Lucknow** | 6h | 17.18 | **15.79** | **0.9304** | **87.1%** | <span style="color:red">**FAIL (< 95%)**</span> |
| **Colombo** | 1h | 6.76 | **6.39** | **0.9878** | **77.4%** | <span style="color:red">**FAIL (< 95%)**</span> |
| **Colombo** | 3h | 9.40 | **9.19** | **0.9764** | **72.0%** | <span style="color:red">**FAIL (< 95%)**</span> |
| **Colombo** | 6h | 11.06 | **10.64** | **0.9673** | **63.4%** | <span style="color:red">**FAIL (< 95%)**</span> |

*Metrics Source:* Evaluated from checkpoint model files and verified in [`metrics/stage4_metrics.json`](file:///c:/Users/PARAM/Desktop/AEGIS/metrics/stage4_metrics.json), [`metrics/stage5_metrics.json`](file:///c:/Users/PARAM/Desktop/AEGIS/metrics/stage5_metrics.json), and [`diagnostics/storm_conditional_conformal_results.csv`](file:///c:/Users/PARAM/Desktop/AEGIS/diagnostics/storm_conditional_conformal_results.csv).

### Known Limitations & Conformal Coverage Failure

> [!CAUTION]
> **Critical Operational Finding:** Conformal prediction intervals lose statistical calibration during geomagnetic storms ($Kp \ge 5$). Across all 12 operational models, empirical storm coverage fell between **63.4% and 87.1%**, severely breaching the nominal 95% safety target. Claims that intervals "eliminate interval breaches" are incorrect.

#### Analysis of Tested Calibration Strategies
In Stage 6, three separate conformal calibration strategies were tested to recover 95% storm coverage:

1. **Validation Slice Calibration ($N = 27$ storm hours):**
   - Calibrating exclusively on storm hours from the chronological validation set produced volatile quantile estimates. While coverage nominally rose for some stations, small-sample noise caused under-coverage for Lucknow 3h (80.6%) and Lucknow 6h (84.9%).
2. **Pooled Out-of-Fold (OOF) Storm Calibration ($N = 300$ storm hours):**
   - Pooling cross-validation storm residuals from training years (2020–2022) resulted in severe coverage collapse on the test set: **37.6% to 66.7%**. Because 2020–2022 was near solar minimum, storm residuals were far smaller than the extreme disturbances seen during the 2023–2024 test window.
3. **Solar Flux $F_{10.7}$-Scaled OOF Regression:**
   - Scaling OOF storm residuals by daily solar radio flux $F_{10.7}$ produced statistically significant scaling ($p < 0.05$), but explained only $1.3\%\text{--}8.9\%$ of residual variance ($R^2 = 0.013\text{--}0.089$). Test storm coverage reached only **58.1% to 86.0%**, failing the 95% benchmark across every single model.

#### Root Cause: Solar-Cycle Non-Stationarity
The failure of fixed conformal prediction during storms stems from **strong temporal distribution shift across the 11-year solar cycle**. 
- The training split (2020–2022) occupied the ascending phase near solar minimum (F10.7 solar flux: 70–120 sfu).
- The test split (2023–2024) entered the active solar maximum of Solar Cycle 25 (F10.7 flux: 150–240+ sfu, frequent G4/G5 storms).
- Because storm peak intensities and plasma fountain amplitudes scale non-linearly with solar cycle phase, any exchangeability assumption between past and future storm errors is violated.

#### Proposed Future Work
1. **Adaptive Rolling-Window Conformal Calibration:** Continuously re-calibrating $\hat{q}$ over a short rolling horizon (e.g., preceding 30–60 days) to adjust for current solar background conditions.
2. **Conformalized Quantile Regression (CQR):** Replacing point estimation with asymmetric pinball loss networks that directly predict state-dependent conditional lower and upper quantiles $\hat{q}_{\alpha/2}(x)$ and $\hat{q}_{1 - \alpha/2}(x)$, conformalizing only the residual quantile errors.

---

## 4. Pipeline Architecture & Vertical Stage Breakdown

1. **Input Sequence (24h Sliding Window):**
   Continuous 24-hour sliding window of solar drivers, geomagnetic indices, and cross-station TEC.
2. **Layer 1 — AttentionBiLSTM (Base Neural Forecaster):**
   Captures diurnal and seasonal trends, applying Luong attention over past hours to generate base forecast $\hat{y}_{\text{lstm}}$.
3. **Layer 2 — XGBoost Residual Stacker (Physics Corrector):**
   Estimates residual error $\hat{e}_{\text{xgb}} = y - \hat{y}_{\text{lstm}}$ using physical electrodynamic features, fountain lags, and storm weights.
4. **Combined Point Forecast:**
   $$\hat{y}_{\text{final}} = \hat{y}_{\text{lstm}} + \hat{e}_{\text{xgb}}$$
5. **Layer 3 — Conformal Prediction Safety Bounds:**
   Wraps point predictions in empirical conformal prediction intervals targeting nominal 95% coverage. *(See Section 3 for verified storm limitations).*

---

## 5. Model Architecture Details

### Layer 1: `AttentionBiLSTM` (Base Model)
- **Bidirectional LSTM:** 2 stacked layers, hidden dimension $H = 128$ per direction ($2 \times 128 = 256$ concatenated feature representation).
- **Luong Dot-Product Attention:** Dynamically weights which of the past 24 hours carry the strongest predictive signal for the forecast horizon.
- **Huber Loss ($\delta = 1.0$):** Applied during training instead of MSE to prevent extreme solar flare gradients from destabilizing network weights.
- **Optimizer & Schedule:** AdamW (`lr = 8.62e-4`), Cosine Annealing learning rate schedule, gradient clipping (`max_norm = 1.0`), and chronological validation early stopping.
- **Dropout Rate:** Training dropout is **0.155** (stored in checkpoints and `best_params`).

### Layer 2: `XGBoost Residual Stacker` (Physics Corrector)
- **Role:** Corrects systematic diurnal biases and non-linear ionospheric fountain delays left by the neural network.
- **Architecture:** 300 gradient-boosted trees, max depth 6, learning rate 0.035, subsample 0.85.
- **Storm-Weighted Training:** Applies up to **15× sample weight** during active space-weather conditions ($Kp \ge 4.5$ or $Dst \le -40\text{ nT}$):
  $$w = 1.0 + 4.0 \cdot \left(\frac{\max(0, Kp - 3)}{3}\right)^2 + 2.0 \cdot \left(\frac{\max(0, -Dst - 30)}{50}\right)$$

### Layer 3: Conformal Prediction Bounds
- **Role:** Computes non-parametric error quantiles $\hat{q}$ at $\alpha = 0.05$ targeting 95% coverage:
  $$\hat{y}_{\text{final}} \pm \hat{q}$$
- **Actual Empirical Quantile Thresholds:**
  - Standard global calibration produces interval half-widths $\hat{q}$ in the range of **$\pm 11.2$ to $\pm 31.2$ TECU** across stations and horizons.
  - Storm-specific calibration yields empirical error quantiles $\hat{q}_{\text{storm}}$ in the range of **$\pm 13.8$ to $\pm 29.0$ TECU** (Bangalore 1h: $\pm 13.8$ TECU, Lucknow 6h: $\pm 20.7$ TECU, Colombo 6h: $\pm 29.0$ TECU).
  - *Correction Note:* Claims that intervals dynamically scale to "$\pm 35$ to $96$ TECU" were artifacts of an uncalibrated synthetic scaling heuristic and do NOT represent verified empirical conformal quantiles.

---

## 6. Input Features

### Layer 1: AttentionBiLSTM Features (12 Features)
- `xray_flux` — GOES-16 solar X-ray radiation flux (0.1–0.8 nm)
- `proton_flux` — GOES-16 energetic proton flux ($>10\text{ MeV}$)
- `solar_wind_speed` — OMNIWeb bulk solar wind velocity ($V_{\text{sw}}$)
- `imf_bz` — Interplanetary Magnetic Field $B_z$ component (GSM coordinates)
- `kp_index` — GFZ Potsdam planetary geomagnetic disturbance index
- `dst_index` — Disturbance Storm Time ring current index
- `hour_of_day` — Diurnal cycle ($0\text{--}23$ UTC)
- `day_of_year` — Annual seasonal cycle ($1\text{--}365$)
- `tec_{station}` — Target station's historical TEC
- `tec_{cross_1, 2, 3}` — Regional cross-station TEC from the other 3 ground stations

### Layer 2: XGBoost Residual Features (25 Features)
- **Base Predictions:** $\hat{y}_{\text{lstm}}$, Predicted Delta $(\hat{y}_{\text{lstm}} - \text{current station TEC})$
- **Cyclic Harmonics:** $\sin/\cos(2\pi\cdot\text{hour}/24)$, $\sin/\cos(2\pi\cdot\text{day}/365.25)$
- **Interplanetary Electric Field:** $E_y = -V_{\text{sw}} \cdot B_z \cdot 10^{-3}\text{ mV/m}$
- **Equatorial Ionization Anomaly (EIA):** Colombo–Station TEC spatial gradient
- **EIA Fountain Transit Lags:** 2-hour and 4-hour lagged EIA gradients (modeling plasma transport delay from magnetic equator to northern crest)
- **Storm Buildup Derivative:** 3-hour $Dst$ drop rate $d(Dst)/dt$
- **Ionospheric Velocity:** 1h and 3h TEC trend slopes for target station and Colombo
- **Space Weather Drivers:** $V_{\text{sw}}$, $B_z$, $Kp$, $Dst$, X-ray flux, Proton flux
- **Regional Telemetry:** Current TEC snapshot across all 4 stations

---

## 7. MC-Dropout Uncertainty vs. Prediction Intervals

- **Scaler Inversion Bug Fix:** In early development, the MC-Dropout code contained a StandardScaler inversion bug that divided standard deviations by `y_sc.scale_[0]` instead of multiplying ($\Delta x = \Delta z \cdot \sigma$), erroneously suppressing output standard deviations to ~0.002 TECU. With the corrected formulation ($\sigma_{\text{tecu}} = \sigma_{\text{latent}} \times \sigma_{\text{target}}$), the AttentionBiLSTM produces a mean standard deviation of **$\sim 3.1$ TECU** across 50 stochastic passes.
- **Epistemic Uncertainty Only:** MC-Dropout captures **epistemic uncertainty** (neural network weight uncertainty across subnetwork ensembles). It does **NOT** capture aleatoric space-weather noise or observation variance, and mean $\sigma \approx 3.1\text{ TECU}$ is significantly smaller than the test RMSE ($\sim 10.5\text{ TECU}$).
- **Not a Calibrated Prediction Interval:** MC-Dropout standard deviation cannot be used as an operational prediction bound. Conformal prediction intervals serve that role, subject to the severe storm limitations documented in Section 3.

---

## 8. Hyperparameter Quick Sheet

- **Lookback Window:** 24 hours
- **BiLSTM Dimension:** 2 stacked layers, `hidden_dim` = 128 (256 concatenated bidirectional features)
- **Training Dropout:** 0.155 (verified in checkpoint dictionary)
- **Optimizer:** AdamW (`lr = 8.62e-4`, weight decay = 1e-4)
- **Loss Function:** Huber Loss ($\delta = 1.0$)
- **XGBoost Regressor:** 300 estimators, max depth 6, learning rate 0.035, subsample 0.85
- **Storm Weighting:** Max 15× sample weight for $Kp \ge 4.5$ or $Dst \le -40\text{ nT}$
