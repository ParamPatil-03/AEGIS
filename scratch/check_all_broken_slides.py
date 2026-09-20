import re

with open('scratch/broken_theme_index.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Find all slides and their full HTML in broken_theme_index.html
slide_divs = list(re.finditer(r'<div class="slide[^"]*" id="([^"]+)"', text))
print(f"Total slides found: {len(slide_divs)}")

for i, m in enumerate(slide_divs):
    start = m.start()
    end = slide_divs[i+1].start() if i+1 < len(slide_divs) else text.find('<!-- FOOTER', start)
    if end == -1: end = start + 3000
    s_html = text[start:end]
    sid = m.group(1)
    
    # Check any inline background, classes, headings
    headings = re.findall(r'<h[1-4][^>]*>([\s\S]*?)</h[1-4]>', s_html)
    clean_heads = [re.sub(r'<[^>]+>', '', h).strip() for h in headings]
    print(f"\n==================== SLIDE {i+1} (id='{sid}') ====================")
    print("Headings:", clean_heads)
    
    # Look for style="background..." or color classes
    colors_found = re.findall(r'style="[^"]*(?:background|color)[^"]*"', s_html)
    print("Inline color/bg count:", len(colors_found))
    if colors_found:
        print("Samples:", colors_found[:3])
