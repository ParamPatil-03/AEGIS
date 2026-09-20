import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Find Slide 8 HTML (id="slide-5")
m = re.search(r'(<div class=["\']slide\b[^"\']*["\']\s+id=["\']slide-5["\'][\s\S]*?)(?=<div class=["\']slide|\Z)', text)
if m:
    s8 = m.group(1)
    print("Slide 8 found! Length:", len(s8))
    # print lines with structure
    for line in s8.splitlines()[:60]:
        print(line)

# Also let's find the CSS for slide 8 (.s6-container, .s6-main-grid, etc.)
style = re.search(r'<style>([\s\S]*?)</style>', text).group(1)
s8_css = []
for block in re.split(r'\}', style):
    if any(k in block for k in ['.s6-', 'slide-5', 'pipeline-', 'inspector-']):
        s8_css.append(block.strip() + '}')

print("\n--- SLIDE 8 CSS ---")
print('\n'.join(s8_css[:25]))
