import re

with open('scratch/commit_55e5970.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Let's extract all CSS rules with 'background' that aren't transparent or dark
css_m = re.search(r'<style>([\s\S]*?)</style>', text)
css = css_m.group(1) if css_m else ''

# Extract rules
rules = re.findall(r'([^{}]*)\{([^{}]*)\}', css)

print("=== ALL CSS RULES WITH SOLID/PROMINENT BACKGROUNDS IN 55e5970 ===")
for sel, body in rules:
    sel = sel.strip().replace('\n', ' ')
    for line in body.split(';'):
        line = line.strip()
        if line.startswith('background') and not any(skip in line for skip in ['transparent', 'none', '#0B0E17', '#0A0B0E', 'rgba(11, 14, 23', 'rgba(255, 255, 255, 0.0']):
            print(f"{sel} ===> {line}")

