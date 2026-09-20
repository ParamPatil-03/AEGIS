import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    head = f.read()

pos = head.find('id="slide-6"')
s9_head = head[pos:]

import re
m = re.search(r'<div class="s7-col-right">([\s\S]*?)</div>\s*</div>\s*</div>', s9_head)
if m:
    print("s7-col-right in HEAD:")
    print(m.group(1)[:600])
