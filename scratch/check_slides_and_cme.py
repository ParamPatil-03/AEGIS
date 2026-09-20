import re

with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    c = f.read()

slides = re.findall(r'<section[^>]*id=["\']([^"\']+)["\']', c)
print('Slides in HEAD:', slides)
print('cme-canvas in HEAD?', 'cme-canvas' in c)
print('sun-canvas in HEAD?', 'sun-canvas' in c)
print('cme-container in HEAD?', 'cme-container' in c)

# Check what was changed in current index.html compared to head
with open('index.html', 'r', encoding='utf-8') as f:
    curr = f.read()

curr_slides = re.findall(r'<section[^>]*id=["\']([^"\']+)["\']', curr)
print('Slides in CURR:', curr_slides)
print('cme-canvas in CURR?', 'cme-canvas' in curr)
print('sun-canvas in CURR?', 'sun-canvas' in curr)
