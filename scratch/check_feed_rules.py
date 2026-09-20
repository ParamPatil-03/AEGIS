import re

with open('index.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

matches = re.findall(r'(\.[^{}]*feed[^{}]*\{[^{}]*\})', text)
print(f"Found {len(matches)} feed rules:")
for m in matches:
    print(m.strip().replace('\n', ' ')[:160])

m2 = re.findall(r'(#[^{}]*slide-data-feeds[^{}]*\{[^{}]*\})', text)
print(f"Found {len(m2)} slide-data-feeds rules:")
for m in m2:
    print(m.strip().replace('\n', ' ')[:160])
