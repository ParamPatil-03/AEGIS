with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    head = f.read()

import re
s9 = re.search(r'(<section[^>]*id=["\']slide-6["\'][\s\S]*?</section>)', head)
if s9:
    print("Slide 9 length:", len(s9.group(1)))
    print("Slide 9 preview (first 1000 chars):")
    print(s9.group(1)[:1000])
    print("\nSlide 9 scripts / canvas mentions:")
    for line in s9.group(1).splitlines():
        if any(k in line.lower() for k in ['canvas', 'three', 'globe', 'sun', 'animation', 'cme']):
            print(line[:120])
