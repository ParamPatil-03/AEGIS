import urllib.request
import re

url = 'https://paralleluniverse.com.ua/wp-content/themes/e-parallel-smooth/assets/css/style.css'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        css = resp.read().decode('utf-8', errors='replace')
        print(f"Downloaded {len(css)} chars of CSS")

        # Find colors: hex, rgba, hsl
        hex_colors = set(re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}\b', css))
        print("Hex colors in style.css:")
        print(sorted(list(hex_colors)))

        # Find font-family
        fonts = set(re.findall(r'font-family\s*:\s*([^;]+);', css))
        print("\nFont families:")
        for f in fonts:
            print(" -", f.strip())

        # Find background colors
        bgs = set(re.findall(r'background(?:-color)?\s*:\s*([^;]+);', css))
        print("\nCommon backgrounds:")
        for b in list(bgs)[:15]:
            print(" -", b.strip())

except Exception as e:
    print("Error fetching CSS:", e)
