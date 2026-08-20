#!/usr/bin/env python3
"""
Ionospheric TEC Data Imputation.
Cleans extreme outliers and fills short gaps (<= 6 hours) using linear interpolation,
flagging the interpolated rows with boolean columns. Leaves longer gaps as NaN.
"""

import os
import pandas as pd
import numpy as np
import logging

def impute_tec_data(file_path):
    """
    Cleans extreme outliers and performs short-gap interpolation in-place.
    """
    logging.info(f"Loading dataset for imputation from {file_path}...")
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return False
        
    df = pd.read_csv(file_path)
    if df.empty:
        logging.warning("Dataset is empty. Skipping imputation.")
        return False

    # Ensure timestamp is treated as string for output matches
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 1. Clean extreme outliers (e.g. values below -50 TECU which are receiver anomalies)
    for col in ['tec_hyderabad', 'tec_bangalore', 'tec_lucknow', 'tec_colombo']:
        if col in df.columns:
            outliers = df[df[col] < -50]
            if not outliers.empty:
                logging.info(f"Replacing {len(outliers)} extreme outliers (<-50) in {col} with NaN...")
                df.loc[df[col] < -50, col] = np.nan

    # 2. Perform short-gap interpolation
    for col in ['tec_hyderabad', 'tec_bangalore', 'tec_lucknow', 'tec_colombo']:
        if col not in df.columns:
            continue
            
        initial_nans = df[col].isna()
        initial_nan_count = initial_nans.sum()
        
        # Linear interpolation for short gaps (up to 6 hours)
        df[col] = df[col].interpolate(method='linear', limit=6)
        
        # Flag interpolated rows
        df[col + '_interpolated'] = initial_nans & df[col].notna()
        interpolated_count = df[col + '_interpolated'].sum()
        remaining_nans = df[col].isna().sum()
        
        logging.info(f"Station {col}:")
        logging.info(f"  Initial NaNs (incl. outliers): {initial_nan_count}")
        logging.info(f"  Interpolated rows: {interpolated_count}")
        logging.info(f"  Remaining NaNs (genuinely missing): {remaining_nans}")

    # Save the updated data
    df.to_csv(file_path, index=False)
    logging.info("Imputation complete and saved successfully.")
    return True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/raw/tec_data.csv")
    impute_tec_data(csv_path)
