import subprocess
import re

for commit in ['507c900', '057b3f7', '55e5970']:
    try:
        out = subprocess.check_output(['git', 'show', f'{commit}:index.html'], text=True, encoding='utf-8', errors='replace')
        slides = re.findall(r'<div class=["\']slide\b[^"\']*["\']\s+id=["\']([^"\']+)["\']', out)
        print(f"Commit {commit} slides:", slides)
    except Exception as e:
        print(f"Commit {commit} error:", e)
