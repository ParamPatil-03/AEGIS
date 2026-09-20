import subprocess

# Inspect slide 8 (slide-6) in 55e5970
out_orig = subprocess.check_output(['git', 'show', '55e5970:index.html'], text=True, encoding='utf-8', errors='replace')
with open('index.html', 'r', encoding='utf-8') as f:
    out_curr = f.read()

import re
# Find slide-6 in both
m1 = re.search(r'<div class="slide" id="slide-6">([\s\S]*?)</div>\s*</div>\s*<!-- END SLIDER', out_orig)
m2 = re.search(r'<div class="slide" id="slide-6">([\s\S]*?)</div>\s*</div>\s*<!-- END SLIDER', out_curr)

print("Original slide-6 length:", len(m1.group(1)) if m1 else "Not found")
print("Current slide-6 length:", len(m2.group(1)) if m2 else "Not found")

# Let's check the HTML difference
if m1 and m2:
    print("Orig controls:\n", "\n".join([line for line in m1.group(1).splitlines() if 'btn' in line or 'label' in line][:15]))
    print("\nCurr controls:\n", "\n".join([line for line in m2.group(1).splitlines() if 'btn' in line or 'label' in line][:15]))
