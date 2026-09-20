with open('index.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re
scripts = re.findall(r'<script[\s\S]*?</script>', text)
print(f"Found {len(scripts)} scripts")

for i, s in enumerate(scripts):
    if 'feed' in s.lower():
        lines = [line.strip() for line in s.splitlines() if any(k in line for k in ['feed-xray', 'className', 'classList', 'updateFeed', 'feed-card'])]
        if lines:
            print(f"Script {i+1} has feed updates:")
            for l in lines[:20]:
                print("  ", l[:120])
