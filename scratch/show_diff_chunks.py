import subprocess

out = subprocess.check_output(['git', 'diff', '55e5970', 'index.html'], text=True, encoding='utf-8', errors='replace')

chunks = out.split('@@ -')
for c in chunks[1:]:
    header = c.split('\n')[0]
    print("="*60)
    print("CHUNK: @@ -" + header)
    lines = c.split('\n')[1:30]
    for l in lines:
        if l.startswith('+') or l.startswith('-'):
            print(l[:100])
