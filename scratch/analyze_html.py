with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

import re
print("Searching for side-link:")
for i, l in enumerate(lines):
    if 'side-link' in l or 'slide' in l.lower() or 'screen' in l.lower() or 'panel' in l.lower() or 'lenis' in l.lower():
        if i < 300 or ('data-slide' in l) or ('side-link' in l and '<' in l):
            print(f"{i+1}: {l.strip()[:100]}")

print("\n--- Event Listeners in JS ---")
for i, l in enumerate(lines):
    if 'addEventListener' in l or 'wheel' in l or 'lenis' in l.lower() or 'scrolltrigger' in l.lower() or 'scrollto' in l.lower():
        print(f"{i+1}: {l.strip()[:100]}")

print("\n--- Sections / Main containers ---")
for i, l in enumerate(lines):
    if '<div class="screen' in l or '<div class="slide' in l or '<div class="panel' in l or '<div class="page' in l or '<section' in l or 'id="screen' in l or 'id="slide' in l or 'id="panel' in l:
        print(f"{i+1}: {l.strip()[:100]}")
