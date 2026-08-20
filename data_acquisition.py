#!/usr/bin/env python3
"""
Data Acquisition Script for Solar/Geomagnetic and Ionospheric TEC Data.
Collects data from 2020-01-01 to 2024-12-31 at hourly resolution.
Saves solar_data.csv and tec_data.csv.
Uses ThreadPoolExecutor for Part 1 (NOAA GOES) and ProcessPoolExecutor for Part 2 (CDDIS)
with process-level global session reuse to bypass redundant OAuth redirect handshakes.
"""

import os
import sys
import time
import re
import logging
import requests
import gzip
import subprocess
import shutil
import numpy as np
import pandas as pd
import xarray as xr
import georinex as gr
from tqdm import tqdm
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from impute_tec import impute_tec_data

# Load environment variables from .env file if it exists
load_dotenv(dotenv_path=os.path.join(os.getcwd(), '.env'))

def setup_logging(log_to_file=True):
    """
    Sets up logging. Only the main process should log to data_acquisition.log
    to avoid file lock issues in child processes on Windows.
    """
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_to_file:
        handlers.append(logging.FileHandler("logs/data_acquisition.log", mode="a", encoding="utf-8"))
        
    for h in logging.root.handlers[:]:
        logging.root.removeHandler(h)
        
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=handlers
    )

# Fallback basic logging for imported processes (console only, no file lock)
logging.basicConfig(level=logging.WARNING, format='%(asctime)s [%(levelname)s] %(message)s')

# Custom Session that preserves Authorization header across redirects to Earthdata Login
class SessionWithHeaderRedirection(requests.Session):
    AUTH_HOST = 'urs.earthdata.nasa.gov'

    def __init__(self, username, password):
        super().__init__()
        self.auth = (username, password)

    def rebuild_auth(self, prepared_request, response):
        """
        Keep authorization headers when redirected to the Earthdata login host.
        """
        headers = prepared_request.headers
        url = prepared_request.url
        if 'Authorization' in headers:
            original_parsed = requests.utils.urlparse(response.request.url)
            redirect_parsed = requests.utils.urlparse(url)
            if (original_parsed.hostname != redirect_parsed.hostname) and \
               redirect_parsed.hostname != self.AUTH_HOST and \
               original_parsed.hostname != self.AUTH_HOST:
                del headers['Authorization']

# Global Cache for NOAA GOES monthly listings
goes_cache = {}

# Global variables inside each worker process
worker_session = None
global_r3_listings = {}

def init_worker(username, password, r3_listings):
    """
    Initializes a global session and directory listings cache for the child process.
    """
    global worker_session, global_r3_listings
    worker_session = SessionWithHeaderRedirection(username, password)
    global_r3_listings = r3_listings

def pre_scrape_goes_listings(start_date, end_date):
    """
    Pre-scrapes NOAA GOES directories for all months in the date range.
    Populates goes_cache.
    """
    logging.info("Pre-scraping NOAA GOES monthly directory listings...")
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)
    months = pd.date_range(start=start_dt, end=end_dt, freq='MS')
    
    def scrape_month(dt):
        year = dt.year
        month_str = f"{dt.month:02d}"
        url = f"https://data.ngdc.noaa.gov/platforms/solar-space-observing-satellites/goes/goes16/l2/data/xrsf-l2-flx1s_science/{year}/{month_str}/"
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                files = re.findall(r'href=["\'](sci_xrsf-l2-flx1s_g16_d\d+_v[^\s"\'>]+)["\']', r.text)
                date_to_file = {}
                for f in files:
                    match = re.search(r'_d(\d{8})_', f)
                    if match:
                        date_to_file[match.group(1)] = f
                return (year, month_str), date_to_file
        except Exception as e:
            logging.error(f"Error pre-scraping GOES listing for {year}/{month_str}: {e}")
        return (year, month_str), {}

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(scrape_month, m): m for m in months}
        for future in as_completed(futures):
            key, val = future.result()
            goes_cache[key] = val
            
    logging.info(f"Pre-scraped {len(goes_cache)} months of GOES listings.")

def get_goes_filename_and_url(date_obj):
    """
    Gets the pre-scraped filename and URL for a date from the cache.
    """
    year = date_obj.year
    month = f"{date_obj.month:02d}"
    day_str = f"{date_obj.year}{date_obj.month:02d}{date_obj.day:02d}"
    
    month_files = goes_cache.get((year, month), {})
    filename = month_files.get(day_str)
    if filename:
        return filename, f"https://data.ngdc.noaa.gov/platforms/solar-space-observing-satellites/goes/goes16/l2/data/xrsf-l2-flx1s_science/{year}/{month}/{filename}"
    return None, None

def process_goes_file(file_path):
    """
    Reads a GOES NetCDF file, extracts 1-minute averaged X-ray flux (0.1-0.8nm band),
    and resamples to hourly mean. Returns a pandas Series.
    """
    try:
        with xr.open_dataset(file_path) as ds:
            flux_var = 'xrsb_flux' if 'xrsb_flux' in ds else 'xrsb' if 'xrsb' in ds else None
            if flux_var is None:
                logging.error(f"GOES file {file_path} does not contain xrsb_flux or xrsb.")
                return None
            
            df = ds[[flux_var]].to_dataframe()
            df = df.rename(columns={flux_var: 'xray_flux'})
            
            if df.index.tz is not None:
                df.index = df.index.tz_convert('UTC').tz_localize(None)
            else:
                df.index = pd.to_datetime(df.index)
            
            df_1min = df.resample('1min').mean()
            df_hourly = df_1min.resample('1h').mean()
            return df_hourly['xray_flux']
    except Exception as e:
        logging.error(f"Error processing GOES file {file_path}: {e}")
        return None

def clean_omni_fill_values(val):
    """
    Cleans OMNIWeb parameter fill values by mapping them to NaN.
    """
    if pd.isna(val):
        return np.nan
    val_abs = abs(val)
    fill_patterns = [99.99, 999.0, 999.9, 9999.0, 99999.0]
    for fp in fill_patterns:
        if abs(val_abs - fp) < 1e-2:
            return np.nan
    return val

def process_single_goes_day(date):
    """
    Thread worker task to process a single day of NOAA GOES data.
    Downloads, processes, caches daily result, and deletes raw NetCDF.
    """
    date_str = date.strftime("%Y%m%d")
    tmp_dir = os.path.abspath("/tmp")
    goes_dir = os.path.join(tmp_dir, "goes")
    goes_processed_dir = os.path.join(tmp_dir, "goes_processed")
    processed_path = os.path.join(goes_processed_dir, f"goes_{date_str}.csv")
    placeholder_404 = os.path.join(goes_processed_dir, f"goes_{date_str}.404")
    
    if os.path.exists(processed_path):
        try:
            day_data = pd.read_csv(processed_path)
            day_data['timestamp'] = pd.to_datetime(day_data['timestamp'])
            return day_data.set_index('timestamp')['xray_flux']
        except Exception:
            pass
            
    if os.path.exists(placeholder_404):
        return None
        
    filename, file_url = get_goes_filename_and_url(date.to_pydatetime())
    if not filename or not file_url:
        with open(placeholder_404, 'w') as f:
            f.write("404")
        return None
        
    local_nc_path = os.path.join(goes_dir, filename)
    
    download_needed = True
    if os.path.exists(local_nc_path) and os.path.getsize(local_nc_path) > 100:
        download_needed = False
        
    if download_needed:
        status = 500
        for attempt in range(3):
            try:
                response = requests.get(file_url, timeout=30, stream=True)
                if response.status_code == 404:
                    status = 404
                    break
                response.raise_for_status()
                
                temp_dest = local_nc_path + f".tmp_{os.getpid()}_{date_str}"
                with open(temp_dest, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                os.replace(temp_dest, local_nc_path)
                status = 200
                break
            except Exception:
                time.sleep(2)
                
        if status == 404:
            with open(placeholder_404, 'w') as f:
                f.write("404")
            return None
        elif status != 200:
            return None
            
    day_series = process_goes_file(local_nc_path)
    if day_series is not None:
        day_df = day_series.to_frame(name='xray_flux')
        day_df.index.name = 'timestamp'
        day_df.to_csv(processed_path)
        
    if os.path.exists(local_nc_path):
        try:
            os.remove(local_nc_path)
        except Exception:
            pass
            
    return day_series

def acquire_solar_data(start_date, end_date):
    """
    Acquires all solar/geomagnetic data (GOES in parallel, OMNIWeb, GFZ Kp) and compiles solar_data.csv.
    """
    logging.info("=== Starting Part 1: Solar/Geomagnetic Data Pipeline ===")
    
    tmp_dir = os.path.abspath("/tmp")
    goes_dir = os.path.join(tmp_dir, "goes")
    goes_processed_dir = os.path.join(tmp_dir, "goes_processed")
    os.makedirs(goes_dir, exist_ok=True)
    os.makedirs(goes_processed_dir, exist_ok=True)
    
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    logging.info("Processing NOAA GOES-16 X-ray Flux...")
    pre_scrape_goes_listings(start_date, end_date)
    
    goes_series_list = []
    max_workers = 10
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_single_goes_day, date): date for date in date_range}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing NOAA GOES Days"):
            res = future.result()
            if res is not None:
                goes_series_list.append(res)
                
    if goes_series_list:
        goes_hourly = pd.concat(goes_series_list).sort_index()
        goes_hourly = goes_hourly[~goes_hourly.index.duplicated(keep='first')]
    else:
        goes_hourly = pd.Series(dtype='float64')
        logging.warning("No NOAA GOES data collected.")
        
    logging.info("Requesting NASA OMNIWeb Hourly Data...")
    omni_url = "https://omniweb.gsfc.nasa.gov/cgi/nx1.cgi"
    start_date_str = start_date.replace("-", "")
    end_date_str = end_date.replace("-", "")
    
    omni_params = [
        ('activity', 'retrieve'),
        ('res', 'hour'),
        ('spacecraft', 'omni2'),
        ('start_date', start_date_str),
        ('end_date', end_date_str),
        ('vars', '18'),
        ('vars', '16'),
        ('vars', '49'),
        ('vars', '38'),
        ('vars', '40')
    ]
    
    omni_records = []
    try:
        r = requests.get(omni_url, params=omni_params, timeout=60)
        r.raise_for_status()
        
        lines = r.text.split('\n')
        data_line_pattern = re.compile(r'^\s*(\d{4})\s+(\d+)\s+(\d+)\s+')
        
        for line in lines:
            match = data_line_pattern.match(line)
            if match:
                parts = line.split()
                if len(parts) == 8:
                    year = int(parts[0])
                    doy = int(parts[1])
                    hour = int(parts[2])
                    
                    ts = pd.to_datetime(f"{year}-{doy:03d} {hour:02d}:00:00", format="%Y-%j %H:%M:%S")
                    
                    solar_wind = clean_omni_fill_values(float(parts[3]))
                    imf_bz = clean_omni_fill_values(float(parts[4]))
                    proton_flux = clean_omni_fill_values(float(parts[5]))
                    kp_index = clean_omni_fill_values(float(parts[6]))
                    dst_index = clean_omni_fill_values(float(parts[7]))
                    
                    if not pd.isna(kp_index):
                        kp_index = kp_index / 10.0
                        
                    omni_records.append({
                        'timestamp': ts,
                        'solar_wind_speed': solar_wind,
                        'imf_bz': imf_bz,
                        'proton_flux': proton_flux,
                        'kp_index': kp_index,
                        'dst_index': dst_index
                    })
        logging.info(f"Successfully parsed {len(omni_records)} records from NASA OMNIWeb.")
    except Exception as e:
        logging.error(f"Error fetching/parsing NASA OMNIWeb data: {e}")
        
    omni_df = pd.DataFrame(omni_records)
    if not omni_df.empty:
        omni_df = omni_df.set_index('timestamp').sort_index()
        omni_df = omni_df[~omni_df.index.duplicated(keep='first')]
    else:
        omni_df = pd.DataFrame(columns=['solar_wind_speed', 'imf_bz', 'proton_flux', 'kp_index', 'dst_index'])
        omni_df.index.name = 'timestamp'
        
    logging.info("Requesting GFZ Potsdam Kp Index...")
    gfz_url = f"https://kp.gfz-potsdam.de/app/json/?start={start_date}T00:00:00Z&end={end_date}T23:59:59Z&index=Kp"
    
    gfz_records = []
    try:
        r = requests.get(gfz_url, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        datetimes = pd.to_datetime(data.get('datetime', []))
        kps = data.get('Kp', [])
        
        for dt, kp in zip(datetimes, kps):
            if dt.tz is not None:
                dt = dt.tz_convert('UTC').tz_localize(None)
            gfz_records.append({
                'timestamp': dt,
                'kp_gfz': float(kp)
            })
        logging.info(f"Parsed {len(gfz_records)} 3-hourly Kp records from GFZ Potsdam.")
    except Exception as e:
        logging.error(f"Error fetching/parsing GFZ Potsdam Kp: {e}")
        
    gfz_df = pd.DataFrame(gfz_records)
    if not gfz_df.empty:
        gfz_df = gfz_df.set_index('timestamp').sort_index()
        gfz_df = gfz_df[~gfz_df.index.duplicated(keep='first')]
    else:
        gfz_df = pd.DataFrame(columns=['kp_gfz'])
        gfz_df.index.name = 'timestamp'
        
    logging.info("Merging solar and geomagnetic data...")
    base_index = pd.date_range(start=f"{start_date} 00:00:00", end=f"{end_date} 23:00:00", freq='h')
    solar_df = pd.DataFrame(index=base_index)
    solar_df.index.name = 'timestamp'
    
    solar_df = solar_df.join(goes_hourly.to_frame(name='xray_flux'), how='left')
    solar_df = solar_df.join(omni_df, how='left')
    solar_df = solar_df.join(gfz_df, how='left')
    
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Saving merged solar data...")
    output_file = "data/raw/solar_data.csv"
    solar_df.to_csv(output_file, index=False)
    logging.info(f"Part 1 complete! Saved merged solar data to {output_file} (shape: {solar_df.shape})")

def calculate_tec_from_dataset(obs):
    """
    Computes TEC in TECU from a loaded georinex Dataset.
    """
    f1 = 1575.42e6
    f2 = 1227.60e6
    C_tecu = (f1**2 * f2**2) / (40.3 * (f1**2 - f2**2)) / 1e16

    if 'sv' not in obs.coords:
        return None
        
    gps_svs = [sv for sv in obs.indexes['sv'] if str(sv).startswith('G')]
    if not gps_svs:
        return None
        
    obs_gps = obs.sel(sv=gps_svs)

    p1_candidates = ['P1', 'C1', 'C1C', 'C1W', 'P1C']
    p2_candidates = ['P2', 'C2', 'C2W', 'C2P', 'C2X', 'C2C']

    p1_var = None
    for cand in p1_candidates:
        if cand in obs_gps.data_vars:
            p1_var = cand
            break
    if p1_var is None:
        for v in obs_gps.data_vars:
            if v.startswith('C1') or v.startswith('P1'):
                p1_var = v
                break

    p2_var = None
    for cand in p2_candidates:
        if cand in obs_gps.data_vars:
            p2_var = cand
            break
    if p2_var is None:
        for v in obs_gps.data_vars:
            if v.startswith('C2') or v.startswith('P2'):
                p2_var = v
                break

    if p1_var is None or p2_var is None:
        return None

    p1_data = obs_gps[p1_var]
    p2_data = obs_gps[p2_var]

    tec_sv = C_tecu * (p2_data - p1_data)
    tec_epoch = tec_sv.mean(dim='sv', skipna=True)
    tec_series = tec_epoch.to_series()
    
    tec_series.index = pd.to_datetime(tec_series.index)
    if tec_series.index.tz is not None:
        tec_series.index = tec_series.index.tz_convert('UTC').tz_localize(None)

    tec_hourly = tec_series.resample('1h').mean()
    return tec_hourly

def decompress_to_rnx(filepath, rinex_dir):
    """
    Decompresses gz/Z/crx files to standard plain-text RINEX file (.rnx).
    Returns the path to the decompressed file, or filepath if it's already decompressed.
    """
    if not filepath or not (filepath.endswith('.gz') or filepath.endswith('.Z') or filepath.endswith('.crx')):
        return filepath
        
    base_name = os.path.basename(filepath)
    unzip_name = base_name
    if unzip_name.endswith('.gz'):
        unzip_name = unzip_name[:-3]
    elif unzip_name.endswith('.Z'):
        unzip_name = unzip_name[:-2]
        
    temp_unzip_path = os.path.join(rinex_dir, f"temp_{os.getpid()}_{unzip_name}")
    
    # Decompress gzip
    if filepath.endswith('.gz'):
        try:
            with gzip.open(filepath, 'rb') as f_in:
                with open(temp_unzip_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        except Exception:
            return filepath
    else:
        # If it is .Z and we don't have unlzw, return original
        return filepath
            
    # If the decompressed file is a Hatanaka compressed file (.crx), decompress it using crx2rnx
    if temp_unzip_path.endswith('.crx') or '.crx' in temp_unzip_path:
        try:
            subprocess.run(['crx2rnx', '-f', temp_unzip_path], capture_output=True)
            if os.path.exists(temp_unzip_path):
                os.remove(temp_unzip_path)
            rnx_path = temp_unzip_path.replace('.crx', '.rnx')
            if os.path.exists(rnx_path):
                return rnx_path
        except Exception:
            if os.path.exists(temp_unzip_path):
                os.remove(temp_unzip_path)
            return filepath
    return temp_unzip_path

def fast_parse_rinex_tec(filepath):
    """
    Ultra-high performance line-by-line RINEX 3 GPS pseudorange observation parser.
    Bypasses georinex/xarray loading overhead to compute mean daily TEC in under 0.2s.
    """
    f1 = 1575.42e6
    f2 = 1227.60e6
    C_tecu = (f1**2 * f2**2) / (40.3 * (f1**2 - f2**2)) / 1e16

    try:
        is_rinex3 = False
        g_obs_types = []
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            # 1. Parse Header
            header_lines = []
            for line in f:
                header_lines.append(line)
                if "END OF HEADER" in line:
                    break
                    
            for line in header_lines:
                if "RINEX VERSION / TYPE" in line:
                    version_str = line.split()[0]
                    if version_str.startswith('3'):
                        is_rinex3 = True
                    break
                    
            if not is_rinex3:
                # Fallback to georinex for RINEX 2
                return None
                
            g_obs_lines = []
            for line in header_lines:
                if "SYS / # / OBS TYPES" in line:
                    if line.strip().startswith('G'):
                        g_obs_lines.append(line)
                    elif g_obs_lines and line.startswith(' '):
                        g_obs_lines.append(line)
                    else:
                        if g_obs_lines and line.strip() and not line.strip().startswith('G') and line.strip()[0].isalpha():
                            break
            
            all_tokens = []
            for line in g_obs_lines:
                tokens = line[6:60].split()
                all_tokens.extend(tokens)
            
            g_obs_types = [t for t in all_tokens if not t.isdigit()]
            
            p1_idx = -1
            p2_idx = -1
            p1_candidates = ['C1C', 'C1W', 'P1C', 'P1', 'C1']
            for cand in p1_candidates:
                if cand in g_obs_types:
                    p1_idx = g_obs_types.index(cand)
                    break
            if p1_idx == -1:
                for idx, t in enumerate(g_obs_types):
                    if t.startswith('C1') or t.startswith('P1'):
                        p1_idx = idx
                        break
                        
            p2_candidates = ['C2W', 'C2P', 'C2X', 'C2C', 'P2', 'C2']
            for cand in p2_candidates:
                if cand in g_obs_types:
                    p2_idx = g_obs_types.index(cand)
                    break
            if p2_idx == -1:
                for idx, t in enumerate(g_obs_types):
                    if t.startswith('C2') or t.startswith('P2'):
                        p2_idx = idx
                        break
                        
            if p1_idx == -1 or p2_idx == -1:
                return None
                
            # 2. Parse Epochs
            current_epoch = None
            current_epoch_svs = []
            epoch_tecs = []
            epoch_timestamps = []
            
            for line in f:
                if line.startswith('>'):
                    if current_epoch and current_epoch_svs:
                        epoch_timestamps.append(current_epoch)
                        epoch_tecs.append(sum(current_epoch_svs) / len(current_epoch_svs))
                        current_epoch_svs = []
                    parts = line[1:].split()
                    try:
                        year = int(parts[0])
                        month = int(parts[1])
                        day = int(parts[2])
                        hour = int(parts[3])
                        minute = int(parts[4])
                        second = int(float(parts[5]))
                        current_epoch = pd.Timestamp(year, month, day, hour, minute, second)
                    except Exception:
                        current_epoch = None
                elif current_epoch and line.startswith('G'):
                    try:
                        p1_start = 3 + p1_idx * 16
                        p2_start = 3 + p2_idx * 16
                        p1_val_str = line[p1_start : p1_start + 14].strip()
                        p2_val_str = line[p2_start : p2_start + 14].strip()
                        if p1_val_str and p2_val_str:
                            p1 = float(p1_val_str)
                            p2 = float(p2_val_str)
                            if p1 > 0 and p2 > 0:
                                tec = C_tecu * (p2 - p1)
                                current_epoch_svs.append(tec)
                    except Exception:
                        pass
            if current_epoch and current_epoch_svs:
                epoch_timestamps.append(current_epoch)
                epoch_tecs.append(sum(current_epoch_svs) / len(current_epoch_svs))
                
        if epoch_timestamps:
            df = pd.DataFrame({'tec': epoch_tecs}, index=epoch_timestamps)
            df.index.name = 'timestamp'
            df_hourly = df.resample('1h').mean()
            return df_hourly['tec']
    except Exception:
        pass
    return None

def process_single_tec_station_day(args):
    """
    Process pool worker task to process a single station-day for TEC.
    Reuses the worker process's global session to avoid repeat OAuth redirects.
    """
    global worker_session, global_r3_listings
    st_name, st_code, date = args
    date_str = date.strftime("%Y%m%d")
    year = date.year
    doy = date.dayofyear
    yy = date.strftime("%y")
    
    tmp_dir = os.path.abspath("/tmp")
    rinex_dir = os.path.join(tmp_dir, "rinex")
    tec_processed_dir = os.path.join(tmp_dir, "tec_processed")
    processed_path = os.path.join(tec_processed_dir, f"{st_name}_{date_str}.csv")
    placeholder_404 = os.path.join(tec_processed_dir, f"{st_name}_{date_str}.404")
    
    # 1. Load from cache if already processed
    if os.path.exists(processed_path):
        try:
            day_tec = pd.read_csv(processed_path)
            day_tec['timestamp'] = pd.to_datetime(day_tec['timestamp'])
            return st_name, day_tec.set_index('timestamp')['tec']
        except Exception:
            pass
            
    if os.path.exists(placeholder_404):
        return st_name, None
        
    # 2. Check local RINEX file or download (try both .gz and .Z)
    local_path = None
    download_success = False
    
    for ext in ['.gz', '.Z']:
        local_filename = f"{st_code}_{date_str}.rnx{ext}"
        candidate_path = os.path.join(rinex_dir, local_filename)
        
        # Check if candidate exists locally
        if os.path.exists(candidate_path) and os.path.getsize(candidate_path) > 100:
            local_path = candidate_path
            download_success = True
            break
            
        file_url = f"https://cddis.nasa.gov/archive/gnss/data/daily/{year}/{doy:03d}/{yy}o/{st_code}{doy:03d}0.{yy}o{ext}"
        
        status = 500
        for attempt in range(3):
            try:
                # Reuse the global authenticated session!
                response = worker_session.get(file_url, timeout=30, stream=True)
                if response.status_code == 404:
                    status = 404
                    break
                response.raise_for_status()
                
                temp_dest = candidate_path + f".tmp_{os.getpid()}_{st_name}_{date_str}"
                with open(temp_dest, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                os.replace(temp_dest, candidate_path)
                status = 200
                break
            except Exception:
                time.sleep(2)
                
        if status == 200:
            local_path = candidate_path
            download_success = True
            break
            
    # Try RINEX 3 if RINEX 2 fails
    if not download_success:
        filenames = global_r3_listings.get((year, doy), [])
        matches = [f for f in filenames if f.lower().startswith(st_code.lower())]
        if matches:
            r3_filename = matches[0]
            ext = ".gz"
            if r3_filename.endswith(".Z"):
                ext = ".Z"
            elif r3_filename.endswith(".zip"):
                ext = ".zip"
            elif r3_filename.endswith(".crx"):
                ext = ".crx"
            elif r3_filename.endswith(".crx.gz"):
                ext = ".crx.gz"
                
            local_filename = f"{st_code}_{date_str}{ext}"
            candidate_path = os.path.join(rinex_dir, local_filename)
            
            if os.path.exists(candidate_path) and os.path.getsize(candidate_path) > 100:
                local_path = candidate_path
                download_success = True
            else:
                file_url = f"https://cddis.nasa.gov/archive/gnss/data/daily/{year}/{doy:03d}/{yy}d/{r3_filename}"
                status = 500
                for attempt in range(3):
                    try:
                        response = worker_session.get(file_url, timeout=30, stream=True)
                        if response.status_code == 404:
                            status = 404
                            break
                        response.raise_for_status()
                        
                        temp_dest = candidate_path + f".tmp_{os.getpid()}_{st_name}_{date_str}"
                        with open(temp_dest, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                        os.replace(temp_dest, candidate_path)
                        status = 200
                        break
                    except Exception:
                        time.sleep(2)
                        
                if status == 200:
                    local_path = candidate_path
                    download_success = True
            
    if not download_success:
        with open(placeholder_404, 'w') as f:
            f.write("404")
        return st_name, None
        
    # 3. Parse and Compute
    result = None
    decompressed_path = None
    try:
        # Try custom high-performance parser on decompressed RINEX
        decompressed_path = decompress_to_rnx(local_path, rinex_dir)
        day_tec_series = fast_parse_rinex_tec(decompressed_path)
        
        # Fallback to georinex if custom parser returns None/errors
        if day_tec_series is None:
            meas_list = ['P1', 'C1', 'C1C', 'C1W', 'P1C', 'P2', 'C2', 'C2W', 'C2P', 'C2X', 'C2C']
            obs = gr.load(local_path, use='G', meas=meas_list)
            day_tec_series = calculate_tec_from_dataset(obs)
            
        if day_tec_series is not None and not day_tec_series.dropna().empty:
            result = day_tec_series
            # Cache successfully processed data
            day_tec_series.reset_index().to_csv(processed_path, index=False)
    except Exception as e:
        print(f"Failed to parse RINEX/compute TEC for {st_name} on {date_str}: {e}")
        
    # Clean up raw download and decompressed temp files
    for p in [local_path, decompressed_path]:
        if p and os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass
                
    return st_name, result

def pre_scrape_r3_directories(start_date, end_date, username, password, stations, tec_processed_dir):
    """
    Pre-scrapes all RINEX 3 daily directories concurrently in the parent process,
    extracting file lists to completely bypass per-task network requests.
    """
    logging.info("Pre-scraping CDDIS daily directory listings for RINEX 3...")
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    needed_dates = []
    for date in date_range:
        date_str = date.strftime("%Y%m%d")
        all_cached = True
        for st_name in stations.keys():
            processed_path = os.path.join(tec_processed_dir, f"{st_name}_{date_str}.csv")
            placeholder_404 = os.path.join(tec_processed_dir, f"{st_name}_{date_str}.404")
            if not os.path.exists(processed_path) and not os.path.exists(placeholder_404):
                all_cached = False
                break
        if not all_cached:
            needed_dates.append(date)
            
    if not needed_dates:
        logging.info("All dates already processed. Skipping pre-scrape.")
        return {}
        
    logging.info(f"Need to check directory listings for {len(needed_dates)} dates.")
    
    r3_listings = {}
    session = SessionWithHeaderRedirection(username, password)
    
    try:
        test_url = "https://cddis.nasa.gov/archive/gnss/data/daily/2024/250/24d/"
        session.get(test_url, timeout=10)
    except Exception:
        pass

    def fetch_doy(dt):
        year = dt.year
        doy = dt.dayofyear
        yy = dt.strftime("%y")
        url = f"https://cddis.nasa.gov/archive/gnss/data/daily/{year}/{doy:03d}/{yy}d/"
        for attempt in range(2):
            try:
                r = session.get(url, timeout=15)
                if r.status_code == 200:
                    links = re.findall(r'href=["\']?([^"\'>]+\.(?:gz|Z|zip|crx))', r.text, re.IGNORECASE)
                    return (year, doy), links
                elif r.status_code == 404:
                    return (year, doy), []
            except Exception:
                time.sleep(2)
        return (year, doy), []

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(fetch_doy, dt): dt for dt in needed_dates}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Pre-scraping CDDIS directories"):
            key, val = future.result()
            if val:
                r3_listings[key] = val
                
    logging.info(f"Successfully pre-scraped {len(r3_listings)} daily listings.")
    return r3_listings

def acquire_tec_data(start_date, end_date):
    """
    Downloads daily RINEX observation files from CDDIS, calculates TEC,
    and compiles tec_data.csv using ProcessPoolExecutor for concurrency.
    Reuses a single persistent HTTP session in each child process.
    """
    logging.info("=== Starting Part 2: Ionospheric TEC Data Pipeline ===")
    
    username = os.environ.get('EARTHDATA_USER')
    password = os.environ.get('EARTHDATA_PASS')
    if not username or not password:
        logging.error("Environment variables EARTHDATA_USER and EARTHDATA_PASS must be set.")
        sys.exit(1)
        
    tmp_dir = os.path.abspath("/tmp")
    rinex_dir = os.path.join(tmp_dir, "rinex")
    tec_processed_dir = os.path.join(tmp_dir, "tec_processed")
    os.makedirs(rinex_dir, exist_ok=True)
    os.makedirs(tec_processed_dir, exist_ok=True)
    
    # Active/proxy GNSS stations archived on the NASA CDDIS network
    # Sourced from Lucknow (lck4) and Colombo, Sri Lanka (sgoc) as EIA anomaly proxy.
    stations = {
        'hyderabad': 'hyde',
        'bangalore': 'iisc',
        'lucknow': 'lck4',
        'colombo': 'sgoc'
    }
    
    base_index = pd.date_range(start=f"{start_date} 00:00:00", end=f"{end_date} 23:00:00", freq='h')
    tec_df = pd.DataFrame(index=base_index, columns=[f'tec_{st}' for st in stations.keys()])
    tec_df.index.name = 'timestamp'
    
    # Pre-scrape directory listings in parent thread pool
    r3_listings = pre_scrape_r3_directories(start_date, end_date, username, password, stations, tec_processed_dir)
    
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    tasks = []
    for date in date_range:
        for st_name, st_code in stations.items():
            tasks.append((st_name, st_code, date))
            
    results_list = []
    
    # Safely utilize 14 cores out of 16 logical processors
    max_workers = min(14, os.cpu_count() or 4)
    logging.info(f"Spawning ProcessPoolExecutor with {max_workers} parallel workers...")
    
    # Initialize child processes with their authenticated global session and the listings cache
    with ProcessPoolExecutor(
        max_workers=max_workers,
        initializer=init_worker,
        initargs=(username, password, r3_listings)
    ) as executor:
        futures = {executor.submit(process_single_tec_station_day, t): t for t in tasks}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing TEC Data"):
            st_name, res = future.result()
            if res is not None:
                results_list.append((st_name, res))
                
    logging.info("Compiling all station data into master dataset...")
    for st_name, res in results_list:
        tec_df.loc[res.index, f'tec_{st_name}'] = res.values
    
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Saving merged TEC data...")
    output_file = "data/raw/tec_data.csv"
    tec_df.to_csv(output_file, index=False)
    logging.info(f"Part 2 complete! Saved raw TEC data to {output_file} (shape: {tec_df.shape})")
    
    # Run hybrid imputation post-processing
    try:
        impute_tec_data(output_file)
    except Exception as e:
        logging.error(f"Error running hybrid imputation: {e}")
    
    print("\n=== Data Acquisition Summary ===")
    for st_name in stations.keys():
        col = f'tec_{st_name}'
        daily_valid = tec_df[col].resample('1D').count()
        successful_days = int((daily_valid > 0).sum())
        total_days = len(daily_valid)
        pct = (successful_days / total_days * 100) if total_days > 0 else 0
        print(f"Station {st_name.capitalize()}: {successful_days}/{total_days} days successfully collected ({pct:.1f}%)")

if __name__ == "__main__":
    setup_logging(log_to_file=True)
    
    start_dt = os.environ.get('START_DATE', '2020-01-01')
    end_dt = os.environ.get('END_DATE', '2024-12-31')
    
    # Start solar data pipeline
    acquire_solar_data(start_dt, end_dt)
    
    username = os.environ.get('EARTHDATA_USER')
    password = os.environ.get('EARTHDATA_PASS')
    if not username or not password:
        logging.warning("=" * 60)
        logging.warning("EARTHDATA_USER or EARTHDATA_PASS environment variables are not set.")
        logging.warning("Skipping Part 2 (Ionospheric TEC data acquisition from NASA CDDIS).")
        logging.warning("To run Part 2, configure your credentials in a .env file or environment.")
        logging.warning("=" * 60)
    else:
        # Start TEC data pipeline
        acquire_tec_data(start_dt, end_dt)
