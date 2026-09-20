import subprocess

out = subprocess.check_output(['git', 'diff', '--stat', '55e5970', 'index.html'], text=True, encoding='utf-8', errors='replace')
print("Diff stat:\n", out)

out = subprocess.check_output(['git', 'diff', '55e5970', 'index.html'], text=True, encoding='utf-8', errors='replace')
lines = out.splitlines()
print(f"Total diff lines: {len(lines)}")
for l in lines:
    if l.startswith('@@'):
        print(l)
