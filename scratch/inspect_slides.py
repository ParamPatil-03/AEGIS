import sys
import re

with open('scratch/commit_55e5970.html', 'r', encoding='utf-8', errors='ignore') as f:
    text_55 = f.read()

out_lines = []

for sid in ['slide-data-feeds', 'slide-2', 'slide-3', 'slide-1']:
    m = re.search(r'(<div class="slide[^"]*" id="' + sid + r'"[\s\S]*?)(?=<div class="slide|\Z)', text_55)
    if m:
        content = m.group(1)
        out_lines.append(f"================== {sid} HTML ==================\n")
        out_lines.append(content[:2500])

out_lines.append("\n================== ALL CSS IN 55e5970 WITH 'color' or 'background' on cards/slides ==================\n")
css_match = re.search(r'<style>([\s\S]*?)</style>', text_55)
if css_match:
    css = css_match.group(1)
    for block in re.findall(r'([^{}]*\{[^{}]*\})', css):
        if any(k in block.lower() for k in ['feed', 'st-card', 'station', 'slide-2', 'slide-3', 'slide-data', 'badge', 'block']):
            out_lines.append(block.strip() + "\n")

with open('scratch/inspect_out.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out_lines))

print("Saved inspect_out.txt successfully")
