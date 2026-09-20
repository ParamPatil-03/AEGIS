import re

with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    head = f.read()

m = re.search(r'(<div class=["\']slide\b[^"\']*["\']\s+id=["\']slide-5["\'][\s\S]*?)(?=<div class=["\']slide|\Z)', head)
if m:
    s8 = m.group(1)
    print("Slide 8 in HEAD length:", len(s8))
    # Check structure
    classes = re.findall(r'class=["\']([^"\']+)["\']', s8)
    print("Top classes in S8:", set(classes[:20]))
