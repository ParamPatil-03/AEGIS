with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
# look for wheel, scroll, Observer, gsap
matches = re.findall(r'(?:addEventListener\([\'"]wheel[\s\S]*?\n\s*\})', text)
for m in matches:
    print("Wheel listener:")
    print(m[:300])

print("\n--- Scroll trigger or navigation in head ---")
lines = text.splitlines()
for i, l in enumerate(lines):
    if any(k in l.lower() for k in ['navigatetoslide', 'gotoslide', 'curindex', 'currentslide']):
        for j in range(max(0, i-5), min(len(lines), i+15)):
            print(f"{j+1}: {lines[j]}")
        break
