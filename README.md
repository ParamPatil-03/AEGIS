# AEGIS — Space Weather & GNSS Positioning Error Forecasting System

> **A real-time AI-powered system that forecasts GPS/GNSS positioning errors caused by space weather events over the Indian subcontinent.**

AEGIS uses an ensemble of deep learning (AttentionBiLSTM) and gradient boosting (XGBoost) models trained on years of ionospheric TEC data, solar wind parameters, and geomagnetic indices. It delivers 1h, 3h, and 6h ahead forecasts for four Indian GNSS ground stations, served through a live web dashboard with real-time NOAA SWPC data ingestion.

---

## Features

- **Real-time solar data ingestion** — Kp index, IMF Bz, solar wind speed, X-ray flux, proton flux, Dst index (from NOAA SWPC — no account required)
- **AI forecasting** — 24 trained models across 4 stations × 3 horizons, with conformal prediction uncertainty bands
- **Live dashboard** — Animated 3D globe, storm alerts, GPS error gauges, data source health monitor
- **No cloud dependency** — Runs entirely on your local machine

---

## ⚠️ Copyright & License Notice

Copyright © 2024 Param Patil. All rights reserved.

This project and its source code, trained model weights, and associated assets are the intellectual property of the author.

- **Personal/educational use** — Allowed with attribution
- **Commercial use** — Not permitted without explicit written permission
- **Redistribution** — Not permitted without explicit written permission
- **Model weights** — The pre-trained model files are provided solely for running this project and may not be used to build derivative products

If you wish to use this project for research, academic work, or any other purpose, please contact: parampatil658@gmail.com

---

## System Requirements

| Requirement | Minimum |
|---|---|
| OS | Windows 10/11, macOS 12+, Ubuntu 20.04+ |
| Python | 3.10 or newer |
| RAM | 4 GB |
| Disk space | ~500 MB (models + data) |
| Internet | Required for live data feeds |

---

## Installation & Setup

### Step 1 — Install Python 3.10+

Download from: https://www.python.org/downloads/

> **Windows users:** During installation, make sure to tick the **"Add Python to PATH"** checkbox before clicking Install.

Verify installation:
```bash
python --version
```

### Step 2 — Clone the Repository

```bash
git clone https://github.com/ParamPatil-03/AEGIS.git
cd AEGIS
```

Or download the ZIP directly from GitHub:
- Click the green **Code** button → **Download ZIP**
- Extract the ZIP to a folder of your choice
- Open a terminal inside that folder

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required libraries including PyTorch, XGBoost, FastAPI, and more. This may take a few minutes depending on your internet speed.

### Step 4 — Download Pre-trained Models

The trained model weights are not stored in the repository (they are large binary files). Run the included download script to fetch them automatically:

```bash
python download_models.py
```

This will download ~44 MB of model weights from GitHub Releases and place them in the `models/` folder. You only need to do this once.

### Step 5 — Run AEGIS

**Windows (easiest):**
Double-click `start_aegis.bat`

**Any OS (terminal):**
```bash
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```

### Step 6 — Open the Dashboard

The browser will open automatically. If it doesn't, navigate to:
```
http://localhost:8000
```

To stop AEGIS, press `Ctrl+C` in the terminal or close the window.

---

## Project Structure

```
AEGIS/
├── api.py                  # FastAPI server — serves dashboard + forecasts + WebSocket
├── live_ingest.py          # Real-time NOAA SWPC data ingestion worker
├── data_acquisition.py     # Historical training data downloader (one-time use)
├── stage1_split.py         # Training pipeline — data split
├── stage4_lstm_v2.py       # Training pipeline — AttentionBiLSTM
├── stage5_ensemble.py      # Training pipeline — XGBoost ensemble
├── stage6_diagnostics.py   # Training pipeline — diagnostics
├── tec_to_gps_error.py     # TEC-to-GPS error conversion
├── download_models.py      # Model weight downloader (run once after cloning)
├── index.html              # Frontend dashboard (single-file)
├── start_aegis.bat         # Windows one-click launcher
├── requirements.txt        # Python dependencies
├── models/                 # Pre-trained model weights (downloaded via download_models.py)
├── data/                   # Live buffer and map data
│   ├── countries_110m.json # GeoJSON for 3D globe
│   ├── live_buffer.csv     # Rolling live data buffer
│   └── processed/          # Training/test datasets (not in repo)
├── diagnostics/            # Model evaluation charts
├── metrics/                # Training metrics JSON
└── fonts/                  # Custom fonts for dashboard
```

---

## Data Sources

All live data is fetched from **publicly available, no-authentication-required** feeds:

| Parameter | Source |
|---|---|
| Kp index | NOAA SWPC |
| Solar wind speed & density | NOAA SWPC / ACE satellite |
| IMF Bz (magnetic field) | NOAA SWPC / ACE satellite |
| X-ray flux (solar flares) | NOAA GOES-16 |
| Dst ring current index | Kyoto World Data Centre |
| F10.7 solar flux | NOAA SWPC |

---

## Monitored Stations

| Station | Location | Lat | Lon |
|---|---|---|---|
| Bangalore | Karnataka, India | 12.97°N | 77.59°E |
| Hyderabad | Telangana, India | 17.37°N | 78.48°E |
| Lucknow | Uttar Pradesh, India | 26.85°N | 80.92°E |
| Colombo | Sri Lanka | 6.93°N | 79.84°E |

---

## Troubleshooting

**"Python is not detected"**
→ Reinstall Python and make sure to tick "Add Python to PATH"

**"No module named uvicorn"**
→ Run `pip install -r requirements.txt` again

**"Model files not found"**
→ Run `python download_models.py`

**Dashboard shows no live data**
→ Check your internet connection. AEGIS needs internet to fetch live NOAA feeds.

**Port 8000 already in use**
→ Run `start_aegis.bat` again — it auto-clears port 8000. Or use: `python -m uvicorn api:app --port 8001`

---

## Contact

**Author:** Param Patil
**Email:** parampatil658@gmail.com
**GitHub:** https://github.com/ParamPatil-03
