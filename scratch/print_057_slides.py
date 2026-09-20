with open('scratch/commit_057b3f7.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re
slides = re.findall(r'<div class="slide[^"]*" id="([^"]+)"', text)
for i, s in enumerate(slides):
    m = re.search(r'<div class="slide[^"]*" id="' + s + r'"[\s\S]*?(?=<div class="slide|\Z)', text)
    h = re.findall(r'<h[1-3][^>]*>(.*?)</h[1-3]>', m.group(0), re.DOTALL) if m else []
    clean_h = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', h[0])) if h else 'No Header'
    print(f"Slide {i+1} (id={s}): {clean_h}")
