import sys
sys.stdout.reconfigure(encoding='utf-8')
import subprocess

out = subprocess.check_output(['git', 'show', '507c900:index.html'], text=True, encoding='utf-8', errors='replace')
pos = out.find('class="stations-track')
print(out[pos:pos+2500])
