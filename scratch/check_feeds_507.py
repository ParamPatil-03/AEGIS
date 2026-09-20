import re

with open('scratch/commit_507c900.html', 'r', encoding='utf-8', errors='ignore') as f:
    text_507 = f.read()

out = []
m = re.search(r'<div class="slide[^"]*" id="slide-data-feeds"[\s\S]*?(?=<div class="slide|\Z)', text_507)
if m:
    out.append("=== SLIDE-DATA-FEEDS HTML IN 507 ===")
    out.append(m.group(0))

css_m = re.search(r'<style>([\s\S]*?)</style>', text_507)
if css_m:
    css = css_m.group(1)
    out.append("\n=== SLIDE-DATA-FEEDS CSS IN 507 ===")
    for rule in re.findall(r'([^{}]*\{[^{}]*\})', css):
        if any(k in rule.lower() for k in ['feed', 's4-container', 'feeds-grid']):
            out.append(rule.strip())

with open('scratch/feeds_507_out.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))
print("Saved scratch/feeds_507_out.txt")
