import requests
import re
import json

def test():
    r = requests.get('https://services.swpc.noaa.gov/products/summary/', timeout=5)
    links = re.findall(r'href=["\']([^"\']+)["\']', r.text)
    interesting = [l for l in links if any(k in l.lower() for k in ['tec', 'iono', 'f10', '10cm', 'flux', 'solar'])]
    print("Interesting links in products/summary/:", interesting)

    # Also check 10cm solar flux
    f10_urls = [
        'https://services.swpc.noaa.gov/products/summary/10cm-flux.json',
        'https://services.swpc.noaa.gov/text/daily-solar-indices.txt',
        'https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json'
    ]
    for u in f10_urls:
        res = requests.get(u, timeout=3)
        print(u, '->', res.status_code, res.text[:80].replace('\n', ' '))

if __name__ == '__main__':
    test()
