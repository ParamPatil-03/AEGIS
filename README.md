# Solar and Ionospheric TEC Data Acquisition Pipeline

This repository contains a Python-based data acquisition pipeline developed for a machine learning project that predicts ionospheric Total Electron Content (TEC) disturbances over India. 

The pipeline collects data from **2020-01-01 to 2024-12-31** at **hourly** resolution:
1. **Solar and geomagnetic indices** (NOAA GOES-16, NASA OMNIWeb, GFZ Potsdam).
2. **Ionospheric TEC data** from 4 ground stations archived at NASA CDDIS: Bangalore (IISC) and Hyderabad (HYDE) as active Indian stations, Lucknow (LCK4) as a North India station, and Colombo, Sri Lanka (SGOC) as a southern Equatorial Ionization Anomaly (EIA) proxy.


---

## Prerequisites

- Python 3.10 or higher.
- A free **NASA Earthdata Login** account to download RINEX data from NASA CDDIS.
  - Register at: [urs.earthdata.nasa.gov](https://urs.earthdata.nasa.gov)
  - Once registered, log in and verify you have checked/approved access for **NASA CDDIS** in your profile applications.

---

## Installation

1. Clone or download this repository to your local system.
2. Open a terminal/command prompt in the project directory.
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

To download RINEX files from NASA CDDIS, you must provide your Earthdata Login credentials. You can set them as environment variables or create a `.env` file in the project root directory.

### Method 1: Using a `.env` file (Recommended)

1. Copy the `.env.example` file to a new file named `.env`:
   - **Command Prompt (Windows)**:
     ```cmd
     copy .env.example .env
     ```
   - **PowerShell (Windows)**:
     ```powershell
     Copy-Item .env.example .env
     ```
   - **Linux/macOS**:
     ```bash
     cp .env.example .env
     ```
2. Open the `.env` file and replace the placeholders with your actual Earthdata username and password:
   ```env
   EARTHDATA_USER=your_real_username
   EARTHDATA_PASS=your_real_password
   ```

### Method 2: Setting Environment Variables in Session

If you prefer not to write your credentials to disk, you can export them directly in your shell session:

#### Windows (Command Prompt)
```cmd
set EARTHDATA_USER=your_username
set EARTHDATA_PASS=your_password
```

#### Windows (PowerShell)
```powershell
$env:EARTHDATA_USER="your_username"
$env:EARTHDATA_PASS="your_password"
```

#### macOS / Linux
```bash
export EARTHDATA_USER="your_username"
export EARTHDATA_PASS="your_password"
```

---

## Running the Pipeline

To run the data acquisition pipeline, simply execute:

```bash
python data_acquisition.py
```

### Script Execution Features
- **Logging**: Detailed logs are written to `data_acquisition.log` in real-time.
- **Resumability**: The script preserves state. If interrupted, running it again will skip already downloaded/processed days, avoiding redundant network requests.
- **Disk Efficiency**: The script downloads raw daily NetCDF and RINEX files (which total ~8 GB), extracts the hourly summaries, saves them locally, and deletes the raw files immediately. This ensures your local disk usage stays below 100 MB at all times.
- **Error Handling & Retries**: Employs robust HTTP requests with 3 retries and a 5-second delay on network timeouts, and writes `.404` placeholders for missing historical dates to prevent re-querying dead links on subsequent runs.

---

## Outputs

Upon successful completion, two clean CSV files are produced in the root directory:

1. **`solar_data.csv`**
   - **Resolution**: Hourly UTC
   - **Columns**: `timestamp`, `xray_flux`, `solar_wind_speed`, `imf_bz`, `proton_flux`, `kp_index`, `dst_index`, `kp_gfz`

2. **`tec_data.csv`**
   - **Resolution**: Hourly UTC
   - **Columns**: `timestamp`, `tec_hyderabad`, `tec_bangalore`, `tec_lucknow`, `tec_colombo`

---

## GNSS Positioning Error Conversion (`tec_to_gps_error.py`)

AEGIS forecasts vertical Total Electron Content (VTEC in TECU). The [`tec_to_gps_error.py`](file:///c:/Users/PARAM/Desktop/AEGIS/tec_to_gps_error.py) module translates VTEC forecasts and conformal safety intervals into operational single-frequency pseudorange delay and positioning error (in meters) for both **GPS L1 (1575.42 MHz)** and **NavIC L5 (1176.45 MHz)**.

### Physical Formulations & Equations
1. **Ionospheric Range Delay:**
   $$\Delta \rho = \frac{40.3 \times (\text{STEC} \times 10^{16})}{f^2}$$
2. **Thin-Shell Slant TEC Mapping:**
   $$z_{\text{shell}} = \arcsin\left( \frac{R_{\text{earth}}}{R_{\text{earth}} + h_{\text{ion}}} \cos(E) \right), \quad M(E) = \frac{1}{\cos(z_{\text{shell}})}, \quad \text{STEC} = \text{VTEC} \times M(E)$$
   *(Parameters: $R_{\text{earth}} = 6371\text{ km}$, $h_{\text{ion}} = 350\text{ km}$).*
3. **Representative Elevation Assumption:**
   Without per-satellite orbital ephemerides, a representative elevation of **$E = 45.0^\circ$** is assumed (mapping factor $M(45^\circ) \approx 1.3475$). This is documented as a simplifying baseline approximation rather than a full multi-satellite least-squares positioning solution.
4. **Single-Frequency Residual Error (0.4 Factor):**
   Standard broadcast ionospheric models (GPS Klobuchar, NavIC NeQuick) typically eliminate ~60% of vertical delay. The remaining unmodeled fraction (~40% or $\text{factor} = 0.4$) maps directly into residual pseudorange position error:
   $$\text{Error}_{\text{position}} \approx \Delta \rho \times 0.4$$
   *(Documented as a literature-based approximation from Klobuchar 1987 & Ho et al. 2002).*
5. **Rate of TEC Index (ROTI):**
   $$\text{ROTI} = \sqrt{\langle (\Delta \text{TEC}/\Delta t)^2 \rangle - \langle \Delta \text{TEC}/\Delta t \rangle^2} \quad [\text{TECU/min}]$$
   - $\text{ROTI} < 0.25$: **Nominal / Quiet** (minimal scintillation risk)
   - $0.25 \le \text{ROTI} < 0.50$: **Moderate** (carrier phase jitter, risk of cycle slips)
   - $\text{ROTI} \ge 0.50$: **Severe** (carrier tracking loss, lock loss risk)

### Execution
Run the sample evaluation across calm and storm events:
```bash
python tec_to_gps_error.py
```
*(Calm single-frequency errors: ~1–5 meters; G4 storm errors: 10–35+ meters).*

---

## FastAPI Operational Serving Backend (`api.py`)

The operational REST API server loads all 12 trained AttentionBiLSTM models and 12 XGBoost residual models into memory on startup and serves live ionospheric and GNSS positioning error forecasts.

### Running the API Server with Uvicorn

Start the local server using `uvicorn`:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Interactive OpenAPI / Swagger documentation is available in your browser at:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### API Endpoints Summary

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| **`/api/health`** | `GET` | Health status and list of all 12 operational models loaded in memory. |
| **`/api/status`** | `GET` | Current space-weather conditions ($Kp$, $B_z$, $Dst$, wind speed) and derived alert level (`CALM`, `WATCH`, `WARNING`, `SEVERE`). |
| **`/api/forecast`** | `GET` | Single station-horizon forecast: `?station=bangalore&horizon=1h`. Returns VTEC, conformal bounds, GPS L1 / NavIC L5 error (m), MC-Dropout sigma, and storm calibration warning. Cached for 5 min. |
| **`/api/forecast/all`** | `GET` | Batch forecast across all 4 stations $\times$ 3 horizons (12 combinations) in one response. |
| **`/api/replay`** | `GET` | Historical storm replay time series: `?event=march_2023_g4&station=lucknow&horizon=1h`. |

### Mandatory Calibration Warning
Every forecast includes a `calibration_warning: bool` field. When $Kp \ge 5.0$, `calibration_warning` is `True` and includes an explicit warning stating that conformal safety bounds lose calibration during geomagnetic storms (dropping from nominal 95% to 63.4%–87.1% coverage).

---

## Real-Time Space Weather Ingestion Worker (`live_ingest.py`)

The real-time ingestion worker [`live_ingest.py`](file:///c:/Users/PARAM/Desktop/AEGIS/live_ingest.py) autonomously streams live space-weather drivers from public NOAA Space Weather Prediction Center (SWPC) feeds to provide operational feature windows for the API.

### NOAA SWPC Real-Time Feeds (No Authentication Required)
1. **Planetary Kp Index**: `https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json`
2. **Solar Wind Plasma ($V_{\text{sw}}$)**: `https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json` *(Active fallback: `products/summary/solar-wind-speed.json` and `json/rtsw/rtsw_wind_1m.json`)*
3. **Solar Wind Magnetic Field (IMF $B_z$ in GSM)**: `https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json` *(Active fallback: `products/summary/solar-wind-mag-field.json` and `json/rtsw/rtsw_mag_1m.json`)*
4. **GOES Solar X-Ray Flux (0.1–0.8 nm)**: `https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json`
5. **Kyoto Dst Index Estimate**: `https://services.swpc.noaa.gov/products/kyoto-dst.json`
6. **GOES Energetic Protons ($\ge 10$ MeV)**: `https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json`

### Key Architecture & Capabilities
- **5-Minute Polling Cycle**: Queries feeds, validates data ranges, strips invalid instrument fill values (e.g., `-999.0`, `-9999.0`), and aggregates to hourly averages.
- **Rolling Lookback Buffer**: Maintains a rolling 24-to-72 hour contiguous feature buffer persisted to disk at `data/live_buffer.csv` and `data/live_buffer_status.json`, ensuring process restarts retain full lookback memory without cold-start data loss.
- **Identical Scaler Parameters**: Uses the exact `StandardScaler` parameters saved inside the PyTorch model checkpoints — never refitting scalers on live data.
- **Graceful Failover & Staleness Detection**:
  - Retries transient failures with exponential backoff (retries $\times 3$).
  - Falls back to last known valid values for transient feed gaps.
  - Automatically flags forecasts as **degraded** (`is_degraded: true`) if any required space-weather feed is stale beyond 3 hours.
- **Station TEC Physical Baseline**: In the absence of real-time ground dual-frequency GNSS receivers streaming RINEX, station TEC values are anchored to regional diurnal baselines indexed by local solar hour.
- **Daemon Integration**: Automatically launched as a background daemon by `api.py` during FastAPI application lifespan startup and gracefully terminated on shutdown. Can also be executed independently via `python live_ingest.py --daemon`.

### Operational Caveat & Data Provenance Notice
> [!IMPORTANT]
> **Data Provenance Caveat (Live SWPC vs. Historical Archives):**
> AEGIS models were trained, validated, and tested on finalized, post-processed historical archives (NASA OMNIWeb, GFZ Potsdam, and NOAA GOES Level-2 data). Operational live data streams from NOAA SWPC Real-Time Solar Wind (RTSW) and quick-look feeds, which utilize automated baseline subtractions, satellite handovers (e.g. DSCOVR to ACE), and near-real-time filtering.
>
> **Live-mode forecasting accuracy has not been formally benchmarked against the historical test-set metrics.** To make this difference completely visible to downstream consumers, every API forecast explicitly includes:
> - `data_source: "live_swpc"` (for live operational forecasts) vs `data_source: "historical"` (for storm replay and test benchmarks).
> - `live_accuracy_caveat`: An operational disclaimer indicating that live SWPC feeds differ in calibration and latency from training data.
> - `is_degraded`: Boolean flag indicating whether any required feed has exceeded the 3-hour staleness threshold.

