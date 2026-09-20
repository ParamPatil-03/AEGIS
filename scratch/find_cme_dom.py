with open('scratch/broken_theme_index.html', 'r', encoding='utf-8') as f:
    broken = f.read()

import re
for m in re.finditer(r'id=[\"\'](cme-[^\"\']+)[\"\']', broken):
    print("Found ID:", m.group(1), "around:", broken[max(0, m.start()-100):min(len(broken), m.end()+100)])
