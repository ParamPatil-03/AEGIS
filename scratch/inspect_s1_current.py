import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect slide 1 HTML
s1_html = re.search(r'(<div class=["\']slide\b[^"\']*["\']\s+id=["\']slide-0["\'][\s\S]*?)(?=<div class=["\']slide|\Z)', text)
print("=== SLIDE 1 HTML ===")
if s1_html:
    print(s1_html.group(1))

# Let's find all CSS rules for slide-0, massive-text, s1-content, flare-graphic
style = re.search(r'<style>([\s\S]*?)</style>', text).group(1)
print("\n=== SLIDE 1 CSS ===")
for block in re.split(r'\}', style):
    if any(k in block for k in ['slide-0', 'massive-text', 's1-content', 's1-sub', 'flare-graphic', 'video-overlay']):
        print(block.strip() + '}\n')
