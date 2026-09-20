import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos_start = text.find('/* --- SLIDE 3: STATIONS --- */')
pos_end = text.find('/* --- SLIDE 4: CHART --- */')

print("=== SLIDE 3 CSS IN CURRENT INDEX.HTML ===")
print(text[pos_start:pos_end].encode('ascii', errors='replace').decode('ascii'))
