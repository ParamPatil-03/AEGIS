<div align="center">
  <h1>AEGIS</h1>
  <h3>Space Weather & GNSS Positioning Error Forecasting System</h3>
  <p>
    <strong>A real-time AI-powered system that forecasts GPS/GNSS positioning errors caused by space weather events over the Indian subcontinent.</strong>
  </p>
</div>

---

## 📖 Table of Contents
1. [Overview](#-overview)
2. [Key Features](#-key-features)
3. [Architecture & Models](#-architecture--models)
4. [Monitored Stations](#-monitored-stations)
5. [Data Sources](#-data-sources)
6. [System Requirements](#-system-requirements)
7. [Installation & Setup](#-installation--setup)
8. [Usage & Dashboard Guide](#-usage--dashboard-guide)
9. [API Documentation](#-api-documentation)
10. [Project Structure](#-project-structure)
11. [Troubleshooting](#-troubleshooting)
12. [License & Copyright](#-license--copyright)
13. [Contact](#-contact)

---

## 🔭 Overview

**AEGIS (Advanced Early-warning GNSS Ionospheric System)** is an operational AI platform designed to predict ionospheric disturbances and the resulting positioning errors in GNSS (Global Navigation Satellite Systems) signals. During severe space weather events—like solar flares and coronal mass ejections (CMEs)—the ionosphere becomes highly turbulent, causing signal delays, scintillations, and lock-loss for GPS receivers on Earth. 

AEGIS uses an ensemble of deep learning (**Attention-based BiLSTM**) and gradient boosting (**XGBoost**) models trained on years of historical ionospheric Total Electron Content (TEC) data, solar wind parameters, and geomagnetic indices. It delivers **1-hour, 3-hour, and 6-hour ahead forecasts** for four critical Indian GNSS ground stations, serving the predictions through a modern, real-time web dashboard.

---

## ✨ Key Features

- **Real-Time Data Ingestion:** Automatically streams live telemetry from NOAA SWPC and ACE satellites (Kp index, IMF Bz, solar wind speed, X-ray flux, proton flux).
- **Hybrid AI Forecasting:** Utilizes 24 dedicated models (AttentionBiLSTM + XGBoost) across 4 stations and 3 forecast horizons.
- **Conformal Prediction:** Provides statistically rigorous uncertainty bands (confidence intervals) for every forecast, ensuring reliability for mission-critical operations.
- **Interactive 3D Dashboard:** Features an animated WebGL globe, real-time space weather alerts, interactive charts (Chart.js), and dynamic GPS error gauges.
- **Historical Replay Mode:** Allows users to simulate past severe geomagnetic storms (e.g., March 2023 G4 storm, May 2024 G5 storm) to analyze system performance.
- **Local & Private:** Runs entirely on your local machine with zero cloud dependency.
- **FastAPI Backend:** High-performance async Python backend for low-latency inference.

---

## 🧠 Architecture & Models

AEGIS operates using a sophisticated data and modeling pipeline:

1. **Data Acquisition:** Live telemetry is ingested continuously by a background thread running in the FastAPI server. Missing data points are imputed on the fly.
2. **Feature Engineering:** Raw solar parameters are transformed into time-series sequences. 
3. **Deep Learning (AttentionBiLSTM):** Captures complex temporal dependencies in space weather data. The attention mechanism helps the model focus on critical moments (e.g., sudden jumps in X-ray flux).
4. **Gradient Boosting (XGBoost):** Acts as a robust ensemble partner, excellent at handling tabular data and non-linear interactions between geomagnetic indices.
5. **Output:** The ensemble predicts the Total Electron Content (TEC), which is then mathematically converted into estimated GNSS positioning error (in meters) based on satellite elevation angles and augmentation modes (like GAGAN/SBAS).

---

## 📍 Monitored Stations

AEGIS provides localized forecasts for the following critical nodes in the Indian subcontinent:

| Station | Location | Lat | Lon | Strategic Importance |
|---|---|---|---|---|
| **Bangalore** | Karnataka, India | 12.97°N | 77.59°E | Near the magnetic equator; high ionospheric scintillation. |
| **Hyderabad** | Telangana, India | 17.37°N | 78.48°E | Key aviation and technological hub. |
| **Lucknow** | Uttar Pradesh, India | 26.85°N | 80.92°E | Northern boundary monitoring. |
| **Colombo** | Sri Lanka | 6.93°N | 79.84°E | Equatorial anomaly crest region. |

---

## 📡 Data Sources

AEGIS relies on high-cadence, publicly available data streams (no API keys required):

| Parameter | Source | Update Frequency | Use Case |
|---|---|---|---|
| **Kp Index** | NOAA SWPC | 3-hour / 1-min estimates | Global geomagnetic storm intensity. |
| **Solar Wind (Speed/Density)** | DSCOVR / ACE | 1-minute | Velocity and pressure of plasma hitting Earth. |
| **IMF Bz** | DSCOVR / ACE | 1-minute | Southward magnetic field (triggers storms). |
| **X-ray Flux** | GOES-16/18 | 1-minute | Solar flare detection and radio blackouts. |
| **Dst Index** | Kyoto WDC | 1-hour | Ring current intensity (equatorial storms). |

---

## 💻 System Requirements

| Component | Minimum Specification | Recommended Specification |
|---|---|---|
| **OS** | Windows 10/11, macOS 12+, Ubuntu 20.04+ | Windows 11 / Ubuntu 22.04 |
| **Python** | 3.10 or newer | Python 3.11+ |
| **RAM** | 4 GB | 8 GB+ |
| **Disk Space** | ~500 MB (models + data) | 1 GB SSD |
| **Network** | Stable internet connection | Broadband (for reliable live ingestion) |

---

## 🚀 Installation & Setup

### 1. 🐍 Install Python
Download Python 3.10+ from [python.org](https://www.python.org/downloads/).
> **Windows users:** Ensure you check **"Add Python to PATH"** during installation.

### 2. 📥 Clone the Repository
```bash
git clone https://github.com/ParamPatil-03/AEGIS.git
cd AEGIS
```

### 3. 📦 Install Dependencies
Install the required libraries (PyTorch, XGBoost, FastAPI, Uvicorn, Pandas, etc.):
```bash
pip install -r requirements.txt
```

### 4. 🧠 Download Pre-trained Models
The trained model weights (~44 MB) are hosted on GitHub Releases. Run the automated script to fetch them:
```bash
python download_models.py
```

### 5. 🚀 Launch the System
**Windows:**
Simply double-click the `start_aegis.bat` file.

**Mac/Linux:**
```bash
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```
The AEGIS models will load in the background, allowing the server to bind instantly. The web dashboard will automatically open at `http://localhost:8000`.

---

## 📊 Usage & Dashboard Guide

Once the dashboard is open, you will see several key modules:
- **Global Status HUD:** Displays the current Kp Index, Solar Wind Speed, and IMF Bz. This is your high-level overview of space weather conditions.
- **3D Interactive Globe:** Visualizes the position of the monitored stations and the Sun's current sub-solar point.
- **Forecast Charts:** Select a station and forecast horizon (1h, 3h, 6h) to view the AI predictions alongside historical data. The shaded regions represent the **Conformal Prediction uncertainty bands**.
- **GPS Error Gauges:** Shows the estimated error in meters for Single Frequency, Dual Frequency, and GAGAN-augmented GNSS receivers.
- **Event Replay:** Use the dropdown in the sidebar to switch from "Live Feed" to historical events like the "March 2023 G4 Storm" to see how the system performs under extreme conditions.

---

## 🔌 API Documentation

AEGIS exposes a fast JSON REST API that you can use to integrate forecasts into other applications (e.g., flight planning software, drone ground control stations).

### 🩺 `GET /health`
Returns the status of the server and model loader.
```json
{
  "status": "ready",
  "loaded_models": 24,
  "device": "cpu"
}
```

### 📈 `GET /api/forecast/all`
Returns the latest forecasts for all stations and all horizons.
**Query Params:**
- `event` (default: "live"): "live", "march_2023_g4", etc.
- `elevation_deg` (default: 45.0): Satellite elevation angle.
- `mode` (default: "single_frequency"): GNSS mode.

### ⏪ `GET /api/replay`
Fetches a full time-series replay for a specific historical storm.
**Query Params:** `event`, `station`, `horizon`, `elevation_deg`, `mode`.

---

## 📁 Project Structure

```text
AEGIS/
├── api.py                  # FastAPI core server & background ingestion
├── live_ingest.py          # Real-time NOAA SWPC data ingestion worker
├── data_acquisition.py     # Historical dataset fetcher (Earthdata API)
├── stage1_split.py         # Data preprocessing pipeline
├── stage4_lstm_v2.py       # AttentionBiLSTM training module
├── stage5_ensemble.py      # XGBoost ensemble training module
├── stage6_diagnostics.py   # Model evaluation & metrics generation
├── tec_to_gps_error.py     # Physics engine: TEC to GNSS error in meters
├── download_models.py      # Fetches .pt and .json models from GitHub Releases
├── index.html              # Frontend web application (HTML/CSS/JS)
├── start_aegis.bat         # Windows quick-start script
├── requirements.txt        # Python dependency manifest
├── models/                 # Directory for downloaded pre-trained models
├── data/                   # Live buffers and GeoJSON assets
├── diagnostics/            # Generated performance plots (PNGs)
└── fonts/                  # UI Typography assets
```

---

## 🛠️ Troubleshooting

- **"Python is not recognized as an internal or external command"**
  Reinstall Python and ensure "Add Python to PATH" is checked.
- **"ModuleNotFoundError: No module named 'uvicorn'"**
  Ensure you ran `pip install -r requirements.txt` in the correct directory/environment.
- **"FileNotFoundError: [Errno 2] No such file or directory: 'models/...'"**
  You forgot to run `python download_models.py`.
- **Port 8000 already in use**
  Run `start_aegis.bat` again (it auto-kills blocking processes), or start the server on a different port: `python -m uvicorn api:app --port 8001`.

---

## ⚠️ License & Copyright

**Copyright © 2024 Param Patil. All rights reserved.**

This project, including its source code, trained model weights, and associated assets, is the intellectual property of the author.
- **Personal/Educational Use:** Allowed with proper attribution.
- **Commercial Use & Redistribution:** Strictly prohibited without explicit written permission.
- **Model Weights:** Provided solely for running this project locally and may not be used to build derivative products.

---

## ✉️ Contact

For research inquiries, commercial licensing, or general questions, please reach out:

- **Author:** Param Patil
- **Email:** parampatil658@gmail.com
- **GitHub:** [ParamPatil-03](https://github.com/ParamPatil-03)

---
<div align="center">
  <i>"Predicting the invisible weather of near-Earth space."</i>
</div>
