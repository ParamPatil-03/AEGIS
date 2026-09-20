import sys
sys.stdout.reconfigure(encoding='utf-8')
import re

with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    head = f.read()

# Let's search for "background:" with colors in head CSS
style = re.search(r'<style>([\s\S]*?)</style>', head).group(1)

# print all rules where background is a color, not transparent or var(--bg)
print("=== HEAD CSS BLOCKS WITH BACKGROUND COLORS ===")
for b in re.split(r'\}', style):
    if 'background:' in b:
        # check if it has accent or hex color or rgb
        for line in b.splitlines():
            if 'background:' in line and not ('var(--bg)' in line or 'transparent' in line or 'none' in line):
                print(b.strip() + '}\n')
                break
