with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    head = f.read()

import re
# check all CSS for st-card, stations-track, val-
for b in re.split(r'\}', head):
    if any(k in b for k in ['.st-card', '.badge-', '.val-crit', '.val-warn', '.val-ok', '.s3-']):
        print(b.strip() + '}\n')
