import urllib.request
import json

endpoints = [
    'http://localhost:8000/api/health',
    'http://localhost:8000/api/status',
    'http://localhost:8000/api/forecast/all?elevation_deg=45.0&mode=single_frequency',
    'http://localhost:8000/api/insights?station=hyderabad&horizon=1h',
    'http://localhost:8000/api/impact?event=march_2023_g4',
    'http://localhost:8000/api/methodology',
    'http://localhost:8000/api/countries-geojson'
]

for url in endpoints:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read()
            print(f"[OK {resp.status}] {url} -> {len(data)} bytes")
    except Exception as e:
        print(f"[FAIL] {url} -> {e}")
