import re

with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    head = f.read()

m = re.search(r'(<div class=["\']slide\b[^"\']*["\']\s+id=["\']slide-0["\'][\s\S]*?)(?=<div class=["\']slide|\Z)', head)
if m:
    print("Length of slide-0 in HEAD:", len(m.group(1)))
    print(m.group(1))
