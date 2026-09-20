import re

with open('index.html', 'r', encoding='utf-8') as f:
    curr = f.read()

m = re.search(r'(<div class=["\']slide\b[^"\']*["\']\s+id=["\']slide-6["\'][\s\S]*?)(?=<div class=["\']slide|\Z)', curr)
if m:
    print("Slide 6 length in curr:", len(m.group(1)))
    # print first 500 chars
    print(m.group(1)[:500])
