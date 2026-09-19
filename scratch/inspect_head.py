import subprocess

out = subprocess.check_output(['git', 'show', 'HEAD:index.html'], text=True, encoding='utf-8')
lines = out.splitlines()

for i, l in enumerate(lines):
    if any(k in l for k in ['slide-data-feeds', 'id="slide-2"', 'id="slide-insights"', 'id="slide-3"']):
        print(f"--- MATCH AT LINE {i}: {l} ---")
        for j in range(max(0, i - 5), min(len(lines), i + 25)):
            print(f"{j}: {lines[j]}")
