# AEGIS Stage 6: Honest Technical Audit & Diagnostics Summary (Post-Fix)

## Executive Reality Check
This document presents the unvarnished findings from an exhaustive statistical diagnostic pass over all 12 operational models (4 stations $\times$ 3 forecast horizons) after implementing **lagged EIA fountain physics**, **storm-weighted residual boosting**, and **locally-adaptive conformal prediction**.

---

## 1. Residual Analysis: Systematic Bias Under Storm Conditions
- **Calm Conditions**: Mean residuals across Indian stations hover near zero ($-0.49$ to $+1.22$ TECU; overall test residuals $-0.49$ to $+0.99$ TECU; Colombo up to $+2.77$ TECU), indicating well-centered baseline predictions during quiet background ionosphere.
- **Storm Conditions ($Kp \ge 5$)**: 
  - The storm-weighted XGBoost residual corrector with EIA fountain lags significantly mitigates the previous systematic underestimation.
  - In particular, **Lucknow 6h** storm bias is substantially reduced to **-2.38 TECU** ($p = 1.399e-01$).
  - **Statistical Significance**: 6 of 12 models exhibit statistically significant differences ($p < 0.05$) between calm and storm residual means.

---

## 2. Error vs. Magnitude: Quintile Analysis
Evaluating RMSE strictly across actual TEC quintiles (Q1 = lowest 20%, Q5 = highest 20% plasma density):
- **Q1 (Low TEC)**: Model errors remain exceptionally low (e.g. Bangalore 1h RMSE = **4.88 TECU**).
- **Q5 (Extreme TEC)**: 
  - Bangalore 6h: Q1 RMSE = **8.00 TECU** vs Q5 RMSE = **9.20 TECU**.
  - Lucknow 6h: Q1 RMSE = **14.13 TECU** vs Q5 RMSE = **19.07 TECU**.

---

## 3. Temporal Autocorrelation: Ljung-Box Test
- **Finding**: Ljung-Box test statistics at lag 10 and 24 are tracked in `diagnostics/temporal_autocorrelation.csv`.
- The addition of short-term TEC trend slopes (`station_tec_trend_1h`, `station_tec_trend_3h`) and Dst drop rate helps damp multi-hour drift during active ionospheric phases.

---

## 4. Worst-Case Failure Analysis: Cluster Dates
Top 10 worst errors across all models:
- **Clustering**: Peak errors remain tied to severe solar storm events:
  - **2023-03-24**: 32 of the top failure events
  - **2023-03-25**: 23 of the top failure events
  - **2023-04-24**: 13 of the top failure events
  - **2023-11-05**: 9 of the top failure events
  - **2023-11-20**: 5 of the top failure events
- Peak single-step absolute error across all models is **115.0 TECU**.

---

## 5. Conformal Prediction Diagnostics: Storm Coverage Breakdown
Across all 12 operational models, standard empirical conformal prediction failed to maintain the nominal 95% safety target during space-weather disturbances:
- **Calm Periods ($Kp < 5$)**: Coverage remained well-calibrated between **92.1%** and **95.9%** (with tight half-widths: $q_{\text{calm}} \approx 11.3\text{--}31.3$ TECU).
- **Storm Periods ($Kp \ge 5$)**: Measured empirical coverage collapsed to between **63.4% and 87.1%** (Hyderabad 1h: 81.7%, Lucknow 6h: 87.1%, Colombo 6h: 63.4%).
- **Multi-Strategy Testing**: Neither validation slice calibration ($N=27$), pooled OOF calibration ($N=300$, yielding 37.6%–66.7%), nor $F_{10.7}$ scaling recovered nominal 95% storm coverage.
- **Audit Conclusion**: Conformal intervals lose exchangeability and calibration during severe geomagnetic storms due to solar-cycle non-stationarity between solar minimum (training) and solar maximum (test).
