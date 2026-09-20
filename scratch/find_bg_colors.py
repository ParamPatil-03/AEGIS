import re

with open('scratch/commit_55e5970.html', 'r', encoding='utf-8', errors='ignore') as f:
    text_orig = f.read()

with open('index.html', 'r', encoding='utf-8', errors='ignore') as f:
    text_curr = f.read()

css_match = re.search(r'<style>([\s\S]*?)</style>', text_orig)
if css_match:
    css = css_match.group(1)
    rules = re.findall(r'([^{}]*\{[^{}]*\})', css)
    print("=== CSS RULES WITH NOTABLE BACKGROUND IN 55e5970 ===")
    for r in rules:
        if 'background' in r:
            for word in ['#8b5cf6', '#3b82f6', '#00e5ff', '#ff8c00', '#e60000', '#10b981', 'linear-gradient', 'var(--accent', 'var(--fg)', 'purple', 'blue', 'yellow', 'gold']:
                if word in r.lower():
                    print("ORIG:", r.strip()[:180])
                    break
