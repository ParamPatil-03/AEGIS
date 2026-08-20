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
