import re

with open('index.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

print("=== STATION CARDS IN HTML ===")
matches = re.findall(r'<div class="st-card[^"]*" id="[^"]+"', text)
for m in matches:
    print(m)

print("\n=== FEED CARDS IN HTML ===")
matches2 = re.findall(r'<div class="feed-card[^"]*" id="[^"]+"', text)
for m in matches2:
    print(m)
