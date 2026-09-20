import re

with open('scratch/broken_theme_index.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Find slides
slides = re.findall(r'<div class="slide[^"]*" id="([^"]+)"', text)
print("Slides:", slides)

# Find CSS rules for slide-data-feeds, slide-2, slide-3, st-card, etc.
css_m = re.search(r'<style>([\s\S]*?)</style>', text)
if css_m:
    css = css_m.group(1)
    rules = re.findall(r'([^{}]*\{[^{}]*\})', css)
    print("\n--- ST-CARD or FEED or SLIDE-2 or SLIDE-3 RULES IN broken_theme_index.html ---")
    for r in rules:
        r_clean = r.strip().replace('\n', ' ')
        for k in ['st-card', 's3-', 'slide-2', 'slide-data-feeds', 'slide-3', 'stations-track', 'feed-card']:
            if k in r_clean:
                print(r_clean[:180])
                break
