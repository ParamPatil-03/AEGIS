with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if any(k in line for k in ['s6-', 'pipeline-stage', 'inspector-card', 'data-sources-strip', 'slide-5']):
        print(f"{i+1}: {line.strip()[:110]}")
