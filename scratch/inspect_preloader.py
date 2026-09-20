with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
preloader = re.search(r'(<!--\s*---\s*PRELOADER[\s\S]*?)(?=<nav\b|<div class=["\']slide|\Z)', text)
if preloader:
    print("Preloader HTML found! Length:", len(preloader.group(1)))
    print(preloader.group(1)[:600])

# check preloader CSS
m_css = re.search(r'(\.preloader\s*\{[\s\S]*?)(?=\/\*|\Z)', text)
if m_css:
    print("\nPreloader CSS:")
    print(m_css.group(1)[:500])

# check preloader JS
m_js = re.search(r'(function\s+initPreloader[\s\S]*?)(?=\n\s*\/\/\s*---|\Z)', text)
if m_js:
    print("\nPreloader JS:")
    print(m_js.group(1)[:500])
