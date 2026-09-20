#!/usr/bin/env python3
"""
AEGIS Model Downloader
======================
Downloads the pre-trained AEGIS model weights from the GitHub Release.
Run this once after cloning the repository.

Usage:
    python download_models.py
"""

import os
import sys
import zipfile
import urllib.request
import urllib.error

RELEASE_URL = "https://github.com/ParamPatil-03/AEGIS/releases/download/v1.0/models.zip"
MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
ZIP_PATH = os.path.join(MODELS_DIR, "models.zip")


def show_progress(block_num, block_size, total_size):
    downloaded = block_num * block_size
    if total_size > 0:
        percent = min(downloaded * 100 / total_size, 100)
        mb_done = downloaded / 1_048_576
        mb_total = total_size / 1_048_576
        bar = "x" * int(percent // 2) + "." * (50 - int(percent // 2))
        print(f"\r  [{bar}] {percent:5.1f}%  {mb_done:.1f}/{mb_total:.1f} MB", end="", flush=True)


def main():
    print("=" * 60)
    print("  AEGIS - Pre-trained Model Downloader")
    print("=" * 60)

    pt_files = [f for f in os.listdir(MODELS_DIR) if f.endswith(".pt")]
    if len(pt_files) >= 12:
        print(f"\n  Models already present ({len(pt_files)} .pt files found). Nothing to download.\n")
        return

    print(f"\n  Downloading models from GitHub Releases...")
    print(f"  URL: {RELEASE_URL}\n")

    os.makedirs(MODELS_DIR, exist_ok=True)

    try:
        urllib.request.urlretrieve(RELEASE_URL, ZIP_PATH, reporthook=show_progress)
        print()
    except urllib.error.HTTPError as e:
        print(f"\n\n  Download failed: HTTP {e.code}")
        print("  Please check: https://github.com/ParamPatil-03/AEGIS/releases")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"\n\n  Network error: {e.reason}")
        sys.exit(1)

    print(f"\n  Extracting models...")
    try:
        with zipfile.ZipFile(ZIP_PATH, "r") as zf:
            members = zf.namelist()
            for i, member in enumerate(members):
                zf.extract(member, MODELS_DIR)
                print(f"\r  Extracting {i+1}/{len(members)}: {os.path.basename(member):<50}", end="")
        print()
    except zipfile.BadZipFile:
        print("\n  Downloaded file is corrupted. Please try again.")
        os.remove(ZIP_PATH)
        sys.exit(1)

    os.remove(ZIP_PATH)
    print(f"\n  All models downloaded and extracted successfully!")
    print(f"  Location: {MODELS_DIR}")
    print("\n  You can now run AEGIS:")
    print("    Windows : double-click start_aegis.bat")
    print("    Terminal: python -m uvicorn api:app --host 127.0.0.1 --port 8000\n")


if __name__ == "__main__":
    main()
