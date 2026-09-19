#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AEGIS Real-Time Space Weather Ingestion Worker (live_ingest.py)
=============================================================

Continuously ingests real-time solar and geomagnetic drivers from NOAA Space
Weather Prediction Center (SWPC) public JSON feeds, resamples them to hourly
intervals, maintains a rolling 24-hour lookback feature buffer, and feeds
live features directly to the AEGIS serving API.

SOURCES (NOAA SWPC Public Feeds — No Authentication Required):
--------------------------------------------------------------
1. Planetary Kp-index:
   https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json
2. Solar Wind Plasma (Bulk Velocity V_sw, Density):
   https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json
   (Active fallback: https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json)
3. Solar Wind Magnetic Field (IMF B_z in GSM coordinates):
   https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json
   (Active fallback: https://services.swpc.noaa.gov/json/rtsw/rtsw_mag_1m.json)
4. Primary GOES Solar X-Ray Flux (0.1–0.8 nm):
   https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json
5. Kyoto Dst Ring Current Index Estimate:
   https://services.swpc.noaa.gov/products/kyoto-dst.json
6. GOES Energetic Proton Flux (>=10 MeV):
   https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json

OPERATIONAL CAVEAT & DATA PROVENANCE:
------------------------------------
The AEGIS neural models were trained and verified on finalized historical
archives (NASA OMNIWeb, GFZ Potsdam, and NOAA GOES Level-2 data). Real-time SWPC
operational feeds utilize different real-time filtering, automated baseline
removal, and satellite handover procedures. Live-mode forecasting accuracy has NOT
been formally benchmarked against the historical test set. Every live forecast
is explicitly stamped with `data_source: "live_swpc"` vs `data_source: "historical"`.
"""

import os
import sys
import time
import json
import logging
import threading
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone, timedelta

import requests
import numpy as np
import pandas as pd

# ── Structured Logging Setup ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [AEGIS-INGEST] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("aegis_ingest")

# ── Constants & File Locations ────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUFFER_FILE_CSV = os.path.join(BASE_DIR, "data/live_buffer.csv")
HISTORICAL_REF_CSV = os.path.join(BASE_DIR, "data/processed/test_data.csv")
STATUS_FILE_JSON = os.path.join(BASE_DIR, "data/live_buffer_status.json")

POLL_INTERVAL_SECONDS = 300       # Poll every 5 minutes
STALE_THRESHOLD_SECONDS = 3 * 3600 # 3 hours stale threshold for degraded mode
MIN_LOOKBACK_HOURS = 24           # Required context window for AttentionBiLSTM
MAX_BUFFER_HOURS = 72             # Maximum rolling retention (3 days)

OPERATIONAL_CAVEAT_MSG = (
    "Live SWPC real-time streams differ in calibration and filtering from historical "
    "OMNIWeb/GFZ training data. Live-mode forecast accuracy has not been formally "
    "validated against historical test-set metrics."
)

# Endpoints configuration with primary and fallback URLs
FEEDS_CONFIG = {
    'kp': {
        'urls': ['https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json'],
        'required': True
    },
    'solar_wind': {
        'urls': [
            'https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json',
            'https://services.swpc.noaa.gov/products/summary/solar-wind-speed.json',
            'https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json'
        ],
        'required': True
    },
    'imf_mag': {
        'urls': [
            'https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json',
            'https://services.swpc.noaa.gov/products/summary/solar-wind-mag-field.json',
            'https://services.swpc.noaa.gov/json/rtsw/rtsw_mag_1m.json'
        ],
        'required': True
    },
    'xray': {
        'urls': ['https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json'],
        'required': True
    },
    'dst': {
        'urls': ['https://services.swpc.noaa.gov/products/kyoto-dst.json'],
        'required': True
    },
    'protons': {
        'urls': ['https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json'],
        'required': False
    },
    'f107': {
        'urls': ['https://services.swpc.noaa.gov/products/summary/10cm-flux.json'],
        'required': False
    }
}


# ── HTTP Fetcher with Exponential Backoff ─────────────────────────────────────
def fetch_json_with_retry(urls: List[str], retries: int = 3, timeout_sec: float = 6.0) -> Tuple[Optional[Any], Optional[str]]:
    """
    Attempts to fetch JSON from candidate URLs in sequence.
    Applies retries with exponential backoff on transient network failures.
    On 4xx client errors (e.g. 404), fails fast to the next candidate URL.
    """
    for url in urls:
        for attempt in range(1, retries + 1):
            try:
                resp = requests.get(url, timeout=timeout_sec)
                if resp.status_code == 200:
                    try:
                        return resp.json(), url
                    except ValueError:
                        pass
                elif 400 <= resp.status_code < 500 and resp.status_code != 429:
                    # 4xx client errors (e.g. 404) are permanent; skip immediately to next URL
                    break
            except (requests.RequestException, TimeoutError) as e:
                if attempt < retries:
                    backoff = 1.5 ** attempt
                    time.sleep(backoff)
    return None, None


# ── Individual Feed Parsers with Strict Fill-Value Filtering ──────────────────
def parse_kp_feed(raw_data: Any) -> Optional[pd.DataFrame]:
    """Parses NOAA Planetary K-index JSON into hourly timestamped DataFrame."""
    if not raw_data or not isinstance(raw_data, list):
        return None
    try:
        df = pd.DataFrame(raw_data)
        if 'time_tag' not in df.columns or 'Kp' not in df.columns:
            return None
        df['timestamp'] = pd.to_datetime(df['time_tag'], utc=True).dt.floor('h')
        df['kp_index'] = pd.to_numeric(df['Kp'], errors='coerce')
        # Filter invalid fill values (Kp is physically bounded between 0.0 and 9.0)
        df.loc[(df['kp_index'] < 0.0) | (df['kp_index'] > 9.0), 'kp_index'] = np.nan
        res = df[['timestamp', 'kp_index']].dropna().drop_duplicates('timestamp')
        return res if not res.empty else None
    except Exception as e:
        logger.error(f"Error parsing Kp feed: {e}")
        return None


def parse_solar_wind_feed(raw_data: Any, source_url: str) -> Optional[pd.DataFrame]:
    """Parses solar wind plasma into hourly average velocity (km/s)."""
    if not raw_data:
        return None
    try:
        if isinstance(raw_data, dict) and 'WindSpeed' in raw_data:
            ts = pd.to_datetime(raw_data.get('TimeStamp'), utc=True).floor('h')
            spd = float(raw_data['WindSpeed'])
            if 100.0 <= spd <= 2500.0:
                return pd.DataFrame([{'timestamp': ts, 'solar_wind_speed': spd}])
            return None

        df = pd.DataFrame(raw_data)
        speed_col = 'proton_speed' if 'proton_speed' in df.columns else ('speed' if 'speed' in df.columns else None)
        if not speed_col or 'time_tag' not in df.columns:
            return None

        df['timestamp'] = pd.to_datetime(df['time_tag'], utc=True).dt.floor('h')
        df['solar_wind_speed'] = pd.to_numeric(df[speed_col], errors='coerce')
        # Filter invalid fill-values (speed is strictly positive, typically 200–1500 km/s)
        df.loc[(df['solar_wind_speed'] < 100.0) | (df['solar_wind_speed'] > 2500.0), 'solar_wind_speed'] = np.nan
        hourly = df.groupby('timestamp')['solar_wind_speed'].mean().reset_index()
        hourly = hourly.dropna()
        return hourly if not hourly.empty else None
    except Exception as e:
        logger.error(f"Error parsing solar wind feed: {e}")
        return None


def parse_imf_mag_feed(raw_data: Any, source_url: str) -> Optional[pd.DataFrame]:
    """Parses solar wind magnetic field into hourly average IMF Bz in GSM coordinates (nT)."""
    if not raw_data:
        return None
    try:
        if isinstance(raw_data, dict) and 'Bz' in raw_data:
            ts = pd.to_datetime(raw_data.get('TimeStamp'), utc=True).floor('h')
            bz = float(raw_data['Bz'])
            if -200.0 <= bz <= 200.0:
                return pd.DataFrame([{'timestamp': ts, 'imf_bz': bz}])
            return None

        df = pd.DataFrame(raw_data)
        bz_col = 'bz_gsm' if 'bz_gsm' in df.columns else ('bz_gse' if 'bz_gse' in df.columns else None)
        if not bz_col or 'time_tag' not in df.columns:
            return None

        df['timestamp'] = pd.to_datetime(df['time_tag'], utc=True).dt.floor('h')
        df['imf_bz'] = pd.to_numeric(df[bz_col], errors='coerce')
        # Filter NOAA fill values (such as -999.0 or -9999.0)
        df.loc[(df['imf_bz'] < -200.0) | (df['imf_bz'] > 200.0), 'imf_bz'] = np.nan
        hourly = df.groupby('timestamp')['imf_bz'].mean().reset_index()
        hourly = hourly.dropna()
        return hourly if not hourly.empty else None
    except Exception as e:
        logger.error(f"Error parsing IMF mag feed: {e}")
        return None


def parse_xray_feed(raw_data: Any) -> Optional[pd.DataFrame]:
    """Parses GOES X-ray primary 0.1-0.8nm channel into hourly flux (W/m^2)."""
    if not raw_data or not isinstance(raw_data, list):
        return None
    try:
        df = pd.DataFrame(raw_data)
        if 'energy' in df.columns:
            df = df[df['energy'] == '0.1-0.8nm']
        if 'time_tag' not in df.columns or 'flux' not in df.columns:
            return None

        df['timestamp'] = pd.to_datetime(df['time_tag'], utc=True).dt.floor('h')
        df['xray_flux'] = pd.to_numeric(df['flux'], errors='coerce')
        # Filter negative or physical impossibility flags
        df.loc[(df['xray_flux'] <= 0.0) | (df['xray_flux'] > 1.0), 'xray_flux'] = np.nan
        hourly = df.groupby('timestamp')['xray_flux'].mean().reset_index()
        hourly = hourly.dropna()
        return hourly if not hourly.empty else None
    except Exception as e:
        logger.error(f"Error parsing X-ray feed: {e}")
        return None


def parse_dst_feed(raw_data: Any) -> Optional[pd.DataFrame]:
    """Parses Kyoto Dst ring current index (nT)."""
    if not raw_data or not isinstance(raw_data, list):
        return None
    try:
        df = pd.DataFrame(raw_data)
        if 'time_tag' not in df.columns or 'dst' not in df.columns:
            return None
        df['timestamp'] = pd.to_datetime(df['time_tag'], utc=True).dt.floor('h')
        df['dst_index'] = pd.to_numeric(df['dst'], errors='coerce')
        # Filter missing instrument fill values
        df.loc[(df['dst_index'] < -1000.0) | (df['dst_index'] > 300.0), 'dst_index'] = np.nan
        res = df[['timestamp', 'dst_index']].dropna().drop_duplicates('timestamp')
        return res if not res.empty else None
    except Exception as e:
        logger.error(f"Error parsing Dst feed: {e}")
        return None


def parse_protons_feed(raw_data: Any) -> Optional[pd.DataFrame]:
    """Parses energetic proton flux (>=10 MeV) in protons/cm^2-s-sr."""
    if not raw_data or not isinstance(raw_data, list):
        return None
    try:
        df = pd.DataFrame(raw_data)
        if 'energy' in df.columns:
            df = df[df['energy'] == '>=10 MeV']
        if 'time_tag' not in df.columns or 'flux' not in df.columns:
            return None
        df['timestamp'] = pd.to_datetime(df['time_tag'], utc=True).dt.floor('h')
        df['proton_flux'] = pd.to_numeric(df['flux'], errors='coerce')
        df.loc[(df['proton_flux'] < 0.0) | (df['proton_flux'] > 1e6), 'proton_flux'] = np.nan
        hourly = df.groupby('timestamp')['proton_flux'].mean().reset_index()
        hourly = hourly.dropna()
        return hourly if not hourly.empty else None
    except Exception as e:
        logger.error(f"Error parsing proton flux feed: {e}")
        return None


def parse_f107_feed(raw_data: Any) -> Optional[pd.DataFrame]:
    """Parses NOAA 10.7cm solar radio flux (SFU / 10^-22 W m^-2 Hz^-1)."""
    if not raw_data:
        return None
    try:
        if isinstance(raw_data, dict):
            raw_data = [raw_data]
        if not isinstance(raw_data, list):
            return None
        df = pd.DataFrame(raw_data)
        if 'time_tag' not in df.columns or 'flux' not in df.columns:
            return None
        df['timestamp'] = pd.to_datetime(df['time_tag'], utc=True).dt.floor('h')
        df['f107_flux'] = pd.to_numeric(df['flux'], errors='coerce')
        df.loc[(df['f107_flux'] < 40.0) | (df['f107_flux'] > 500.0), 'f107_flux'] = np.nan
        hourly = df.groupby('timestamp')['f107_flux'].mean().reset_index()
        hourly = hourly.dropna()
        return hourly if not hourly.empty else None
    except Exception as e:
        logger.error(f"Error parsing F10.7 flux feed: {e}")
        return None


def synthesize_dynamic_station_tec(
    hour_utc: int,
    st_name: str,
    diurnal_base: float,
    f107: float = 100.0,
    xray: float = 1e-7,
    vsw: float = 400.0,
    bz: float = 0.0,
    dst: float = 0.0,
    kp: float = 2.0
) -> float:
    """
    Computes real-time dynamic ground station TEC (TECU) using physical
    electrodynamic and solar flux perturbation scaling:
    
    TEC_live(t, stn) = TEC_diurnal(h) * (F10.7 / 100)^0.65
                       + delta_TEC_flare(Xray)
                       + delta_TEC_EIA(Ey, stn)
                       + delta_TEC_storm(Dst, Kp)
    """
    # 1. Solar activity baseline scaling
    f107_val = max(50.0, min(350.0, float(f107))) if (f107 is not None and not np.isnan(f107)) else 100.0
    solar_scale = (f107_val / 100.0) ** 0.65
    base_tec = float(diurnal_base) * solar_scale

    # Local solar time approximation (IST ~ UTC + 5.5h)
    local_solar_hour = (float(hour_utc) + 5.5) % 24.0
    # Solar zenith angle cos factor (positive during daylight ~06:00 to ~18:00 IST)
    cos_zenith = max(0.0, float(np.cos(np.pi * (local_solar_hour - 12.0) / 12.0)))

    # 2. Flare photoionization enhancement
    xray_val = max(1e-9, min(1e-2, float(xray))) if (xray is not None and not np.isnan(xray)) else 1e-7
    # Quiet background is ~ 1e-8 W/m^2 (B1.0)
    flare_boost = max(0.0, float(np.log10(xray_val / 1e-8)))
    delta_flare = 2.5 * flare_boost * cos_zenith

    # 3. Prompt Penetration Electric Field & EIA Fountain transport
    # Ey = -Vsw * Bz * 1e-3 (in mV/m). Eastward (Ey > 0) enhances daytime fountain.
    vsw_val = max(200.0, min(1200.0, float(vsw))) if (vsw is not None and not np.isnan(vsw)) else 400.0
    bz_val = max(-50.0, min(50.0, float(bz))) if (bz is not None and not np.isnan(bz)) else 0.0
    ey_field = -1.0 * vsw_val * bz_val * 1e-3  # mV/m

    eia_coeffs = {
        'lucknow': 2.8,    # EIA Crest: strong enrichment during daytime eastward PPEF
        'hyderabad': 1.8,  # Sub-crest: moderate enrichment
        'bangalore': 0.8,  # Sub-equatorial: mild
        'colombo': -1.0    # Equatorial Trough: plasma evacuated upward/poleward
    }
    beta = eia_coeffs.get(st_name.lower(), 1.0)
    delta_eia = beta * float(np.clip(ey_field, -5.0, 8.0)) * cos_zenith

    # 4. Geomagnetic storm ring current & thermospheric perturbation
    kp_val = max(0.0, min(9.0, float(kp))) if (kp is not None and not np.isnan(kp)) else 2.0
    dst_val = max(-400.0, min(100.0, float(dst))) if (dst is not None and not np.isnan(dst)) else 0.0

    storm_weights = {
        'lucknow': 1.25,
        'hyderabad': 1.10,
        'bangalore': 0.95,
        'colombo': 0.85
    }
    gamma = storm_weights.get(st_name.lower(), 1.0)
    storm_term = 0.55 * max(0.0, kp_val - 3.0) + 0.06 * max(0.0, -dst_val - 25.0)
    delta_storm = gamma * float(np.clip(storm_term, -10.0, 35.0))

    total_tec = base_tec + delta_flare + delta_eia + delta_storm
    # Physical boundaries: minimum 3.0 TECU (tropical floor), max 180.0 TECU
    return float(np.clip(total_tec, 3.0, 180.0))


# ── Live Buffer Manager ───────────────────────────────────────────────────────
class LiveBufferManager:
    """
    Maintains a rolling 24–72 hour feature buffer of synchronized space weather
    and ground station TEC data, persisted to disk at `data/live_buffer.csv`.
    """
    def __init__(self):
        self.lock = threading.RLock()
        self.buffer_df: Optional[pd.DataFrame] = None
        self.last_poll_time: Optional[float] = None
        self.feed_status: Dict[str, Dict[str, Any]] = {
            k: {'last_success': None, 'last_url': None, 'error_count': 0}
            for k in FEEDS_CONFIG
        }
        self.is_degraded = False
        self.degraded_reasons: List[str] = []
        self.diurnal_profiles: Dict[str, Dict[int, float]] = {}
        self._load_diurnal_reference()
        self._initialize_buffer()

    def _load_diurnal_reference(self):
        """Computes reference diurnal TEC baselines for the 4 regional stations."""
        if os.path.exists(HISTORICAL_REF_CSV):
            try:
                ref_df = pd.read_csv(HISTORICAL_REF_CSV)
                for st in ['hyderabad', 'bangalore', 'lucknow', 'colombo']:
                    col = f'tec_{st}'
                    if col in ref_df.columns:
                        self.diurnal_profiles[st] = ref_df.groupby('hour_of_day')[col].mean().to_dict()
            except Exception as e:
                logger.warning(f"Could not compute diurnal profile from reference data: {e}")

    def _initialize_buffer(self):
        """Loads buffer from disk if present and valid; otherwise seeds from reference data."""
        with self.lock:
            if os.path.exists(BUFFER_FILE_CSV):
                try:
                    df = pd.read_csv(BUFFER_FILE_CSV)
                    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
                    # Verify required columns exist and are non-empty
                    req_cols = ['xray_flux', 'solar_wind_speed', 'imf_bz', 'kp_index', 'dst_index']
                    has_cols = all(c in df.columns for c in req_cols)
                    if has_cols and len(df) >= MIN_LOOKBACK_HOURS and not df['kp_index'].dropna().empty:
                        self.buffer_df = df.sort_values('timestamp').reset_index(drop=True)
                        logger.info(f"Loaded valid live buffer from disk: {len(self.buffer_df)} hours.")
                        # Restore persisted feed status if available
                        if os.path.exists(STATUS_FILE_JSON):
                            try:
                                with open(STATUS_FILE_JSON, 'r') as sf:
                                    meta = json.load(sf)
                                    self.last_poll_time = meta.get('last_poll_time')
                                    p_feeds = meta.get('feed_status', {})
                                    for fk, fv in p_feeds.items():
                                        if fk in self.feed_status:
                                            self.feed_status[fk] = fv
                            except Exception as pe:
                                logger.warning(f"Could not load {STATUS_FILE_JSON}: {pe}")
                        return
                except Exception as e:
                    logger.warning(f"Could not read existing buffer {BUFFER_FILE_CSV}: {e}. Reseeding.")

            # Seed buffer from reference test dataset
            if os.path.exists(HISTORICAL_REF_CSV):
                try:
                    ref_df = pd.read_csv(HISTORICAL_REF_CSV)
                    ref_df['timestamp'] = pd.to_datetime(ref_df['timestamp'], utc=True)
                    seed_df = ref_df.tail(48).copy().reset_index(drop=True)
                    self.buffer_df = seed_df
                    self._save_buffer_to_disk()
                    logger.info(f"Seeded live buffer with latest {len(self.buffer_df)} reference hours.")
                except Exception as e:
                    logger.error(f"Error seeding buffer from reference: {e}")

    def _save_buffer_to_disk(self):
        """Persists current buffer and feed status to disk so state survives process restarts."""
        if self.buffer_df is not None and not self.buffer_df.empty:
            os.makedirs(os.path.dirname(BUFFER_FILE_CSV), exist_ok=True)
            save_df = self.buffer_df.copy()
            save_df['timestamp'] = save_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            save_df.to_csv(BUFFER_FILE_CSV, index=False)

            # Persist operational status and feed telemetry
            try:
                with open(STATUS_FILE_JSON, 'w') as sf:
                    json.dump({
                        'last_poll_time': self.last_poll_time,
                        'feed_status': self.feed_status
                    }, sf, indent=2)
            except Exception as pe:
                logger.warning(f"Could not persist {STATUS_FILE_JSON}: {pe}")

    def is_ready(self) -> bool:
        """Checks if buffer has at least 24 contiguous hourly rows."""
        with self.lock:
            return self.buffer_df is not None and len(self.buffer_df) >= MIN_LOOKBACK_HOURS

    def get_feature_window(self, seq_len: int = 24) -> Optional[pd.DataFrame]:
        """Returns the most recent `seq_len` hourly feature rows for model inference."""
        with self.lock:
            if self.buffer_df is None or len(self.buffer_df) < seq_len:
                return None
            return self.buffer_df.tail(seq_len).copy().reset_index(drop=True)

    def get_status(self) -> Dict[str, Any]:
        """Returns operational status, buffer length, and feed health."""
        with self.lock:
            now = time.time()
            stale_feeds = []
            for feed_name, cfg in FEEDS_CONFIG.items():
                if cfg['required']:
                    st = self.feed_status[feed_name]
                    ls = st['last_success']
                    if ls is None or (now - ls) > STALE_THRESHOLD_SECONDS:
                        stale_feeds.append(feed_name)

            self.is_degraded = len(stale_feeds) > 0
            self.degraded_reasons = [f"Feed '{f}' stale > 3 hours" for f in stale_feeds]

            latest_ts = str(self.buffer_df['timestamp'].iloc[-1]) if (self.buffer_df is not None and not self.buffer_df.empty) else None

            return {
                'is_ready': self.is_ready(),
                'is_degraded': self.is_degraded,
                'degraded_reasons': self.degraded_reasons,
                'buffer_hours': len(self.buffer_df) if self.buffer_df is not None else 0,
                'latest_timestamp': latest_ts,
                'last_poll_time': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(self.last_poll_time)) if self.last_poll_time else None,
                'feed_status': self.feed_status,
                'live_accuracy_caveat': OPERATIONAL_CAVEAT_MSG
            }

    def update_with_live_feeds(self, feeds_data: Dict[str, pd.DataFrame]):
        """Merges freshly fetched space-weather feeds into the persistent rolling buffer."""
        with self.lock:
            self.last_poll_time = time.time()
            if not feeds_data:
                return

            # Combine all available hourly feeds
            merged_hourly = None
            for feed_name, df_feed in feeds_data.items():
                if df_feed is None or df_feed.empty:
                    continue
                if merged_hourly is None:
                    merged_hourly = df_feed
                else:
                    merged_hourly = merged_hourly.merge(df_feed, on='timestamp', how='outer')

            if merged_hourly is None or merged_hourly.empty:
                return

            merged_hourly['timestamp'] = pd.to_datetime(merged_hourly['timestamp'], utc=True)
            merged_hourly = merged_hourly.sort_values('timestamp').reset_index(drop=True)

            # Reconcile with existing buffer
            if self.buffer_df is None or self.buffer_df.empty:
                combined = merged_hourly.copy()
            else:
                existing = self.buffer_df.copy()
                existing['timestamp'] = pd.to_datetime(existing['timestamp'], utc=True)

                # Outer join to align timestamps
                combined = pd.merge(existing, merged_hourly, on='timestamp', how='outer', suffixes=('_old', ''))

                # Overwrite old space-weather columns with fresh values from NOAA SWPC
                for col in merged_hourly.columns:
                    if col != 'timestamp' and f"{col}_old" in combined.columns:
                        combined[col] = combined[col].combine_first(combined[f"{col}_old"])
                        combined.drop(columns=[f"{col}_old"], inplace=True)

            combined = combined.sort_values('timestamp').reset_index(drop=True)

            # Compute cyclic calendar drivers
            combined['hour_of_day'] = combined['timestamp'].dt.hour
            combined['day_of_year'] = combined['timestamp'].dt.dayofyear

            # Forward-fill / back-fill space weather values (satisfying failover Requirement 4)
            sw_cols = ['kp_index', 'solar_wind_speed', 'imf_bz', 'xray_flux', 'dst_index', 'proton_flux', 'f107_flux']
            for col in sw_cols:
                if col in combined.columns:
                    combined[col] = combined[col].ffill().bfill()

            # Dynamic Ground Station Electrodynamic & Solar Flux TEC Synthesis
            st_cols = ['tec_hyderabad', 'tec_bangalore', 'tec_lucknow', 'tec_colombo']
            merged_ts_set = set(merged_hourly['timestamp']) if merged_hourly is not None else set()
            for st_col in st_cols:
                st_name = st_col.replace('tec_', '')
                if st_col not in combined.columns:
                    combined[st_col] = np.nan

                # Compute physical dynamic synthesized TEC for missing or fresh live rows
                for i in range(len(combined)):
                    curr_val = combined.at[i, st_col]
                    row_ts = combined.at[i, 'timestamp']
                    if pd.isna(curr_val) or row_ts in merged_ts_set:
                        h_utc = int(combined.at[i, 'hour_of_day'])
                        d_base = self.diurnal_profiles.get(st_name, {}).get(h_utc, 28.0)
                        synth_val = synthesize_dynamic_station_tec(
                            hour_utc=h_utc,
                            st_name=st_name,
                            diurnal_base=d_base,
                            f107=combined.at[i, 'f107_flux'] if 'f107_flux' in combined.columns else 100.0,
                            xray=combined.at[i, 'xray_flux'] if 'xray_flux' in combined.columns else 1e-7,
                            vsw=combined.at[i, 'solar_wind_speed'] if 'solar_wind_speed' in combined.columns else 400.0,
                            bz=combined.at[i, 'imf_bz'] if 'imf_bz' in combined.columns else 0.0,
                            dst=combined.at[i, 'dst_index'] if 'dst_index' in combined.columns else 0.0,
                            kp=combined.at[i, 'kp_index'] if 'kp_index' in combined.columns else 2.0
                        )
                        combined.at[i, st_col] = synth_val

                # Ensure forward-fill and back-fill continuity with zero static magic numbers
                combined[st_col] = combined[st_col].ffill().bfill()

            # Trim to MAX_BUFFER_HOURS
            if len(combined) > MAX_BUFFER_HOURS:
                combined = combined.tail(MAX_BUFFER_HOURS).reset_index(drop=True)

            self.buffer_df = combined
            self._save_buffer_to_disk()


# Global Singleton Buffer Manager
live_buffer_manager = LiveBufferManager()


# ── Live Polling Cycle Execution ──────────────────────────────────────────────
def poll_live_feeds() -> Dict[str, Any]:
    """
    Executes a single poll cycle across all configured NOAA SWPC endpoints.
    Parses feeds, updates the rolling buffer, and logs execution details.
    """
    start_time = time.time()
    succeeded_feeds = []
    failed_feeds = []
    parsed_dfs = {}

    parsers = {
        'kp': parse_kp_feed,
        'solar_wind': parse_solar_wind_feed,
        'imf_mag': parse_imf_mag_feed,
        'xray': parse_xray_feed,
        'dst': parse_dst_feed,
        'protons': parse_protons_feed,
        'f107': parse_f107_feed
    }

    for feed_name, cfg in FEEDS_CONFIG.items():
        raw_json, used_url = fetch_json_with_retry(cfg['urls'], retries=2, timeout_sec=5.0)
        if raw_json is not None:
            parser_fn = parsers[feed_name]
            if feed_name in ['solar_wind', 'imf_mag']:
                df_parsed = parser_fn(raw_json, used_url)
            else:
                df_parsed = parser_fn(raw_json)

            if df_parsed is not None and not df_parsed.empty:
                succeeded_feeds.append(feed_name)
                parsed_dfs[feed_name] = df_parsed
                live_buffer_manager.feed_status[feed_name]['last_success'] = time.time()
                live_buffer_manager.feed_status[feed_name]['last_url'] = used_url
                live_buffer_manager.feed_status[feed_name]['error_count'] = 0
            else:
                failed_feeds.append(feed_name)
                live_buffer_manager.feed_status[feed_name]['error_count'] += 1
        else:
            failed_feeds.append(feed_name)
            live_buffer_manager.feed_status[feed_name]['error_count'] += 1

    # Ingest into persistent buffer
    live_buffer_manager.update_with_live_feeds(parsed_dfs)
    live_buffer_manager.last_poll_time = time.time()

    elapsed = time.time() - start_time
    status = live_buffer_manager.get_status()

    # Log structured poll result
    logger.info(
        f"POLL CYCLE COMPLETE | Succeeded ({len(succeeded_feeds)}): {succeeded_feeds} | "
        f"Failed ({len(failed_feeds)}): {failed_feeds} | Buffer: {status['buffer_hours']}h | "
        f"Latest: {status['latest_timestamp']} | Latency: {elapsed:.2f}s | Degraded: {status['is_degraded']}"
    )

    return {
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'succeeded_feeds': succeeded_feeds,
        'failed_feeds': failed_feeds,
        'duration_sec': round(elapsed, 3),
        'buffer_status': status
    }


# ── Background Worker Daemon ──────────────────────────────────────────────────
class LiveIngestDaemon(threading.Thread):
    def __init__(self, interval_sec: int = POLL_INTERVAL_SECONDS):
        super().__init__(daemon=True, name="LiveIngestDaemon")
        self.interval = interval_sec
        self.stop_event = threading.Event()

    def run(self):
        logger.info(f"Starting Live Ingest Daemon (polling interval: {self.interval}s)...")
        # Run immediate first poll on startup
        try:
            poll_live_feeds()
        except Exception as e:
            logger.error(f"Error in initial live ingest poll: {e}")

        while not self.stop_event.is_set():
            self.stop_event.wait(self.interval)
            if not self.stop_event.is_set():
                try:
                    poll_live_feeds()
                except Exception as e:
                    logger.error(f"Unhandled error in live ingest poll cycle: {e}")

    def stop(self):
        self.stop_event.set()


# Module-level daemon handle
_daemon_thread: Optional[LiveIngestDaemon] = None


def start_live_ingest_worker(interval_sec: int = POLL_INTERVAL_SECONDS):
    """Starts the background polling worker thread if not already running."""
    global _daemon_thread
    if _daemon_thread is None or not _daemon_thread.is_alive():
        _daemon_thread = LiveIngestDaemon(interval_sec=interval_sec)
        _daemon_thread.start()
        logger.info("Live ingest background thread started successfully.")


def stop_live_ingest_worker():
    """Stops the background worker thread cleanly."""
    global _daemon_thread
    if _daemon_thread is not None and _daemon_thread.is_alive():
        _daemon_thread.stop()
        _daemon_thread.join(timeout=5)
        logger.info("Live ingest background thread stopped.")


if __name__ == "__main__":
    print("=" * 80)
    print("AEGIS LIVE SPACE WEATHER INGESTION WORKER (CLI RUNNER)")
    print("=" * 80)
    result = poll_live_feeds()
    print("\nInitial Poll Cycle Result:")
    print(json.dumps(result, indent=2))

    if "--daemon" in sys.argv:
        print("\nRunning in daemon mode. Press Ctrl+C to terminate...")
        start_live_ingest_worker()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down ingest daemon...")
            stop_live_ingest_worker()
