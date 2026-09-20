import re

with open('scratch/commit_507c900.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

slides = re.findall(r'<div class="slide[^"]*" id="([^"]+)"', text)
print('Slides in 507c900:', slides)

for i, sid in enumerate(slides):
    m = re.search(r'<div class="slide[^"]*" id="' + sid + r'"[\s\S]*?(?=<div class="slide|\Z)', text)
    if m:
        s_text = m.group(0)
        print(f"\n--- SLIDE {i+1}: {sid} ---")
        h2 = re.findall(r'<h[1-3][^>]*>(.*?)</h[1-3]>', s_text, re.DOTALL)
        print("Headers:", [h.strip().replace('\n', ' ') for h in h2])
        # Find elements with style background or classes
        bg_inline = re.findall(r'style="[^"]*background[^"]*"', s_text)
        if bg_inline:
            print("Inline backgrounds:", bg_inline[:5])
