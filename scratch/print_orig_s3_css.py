import sys
sys.stdout.reconfigure(encoding='utf-8')
import re

with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    head = f.read()

pos_start = head.find('/* --- SLIDE 3: STATIONS --- */')
pos_end = head.find('/* --- SLIDE 4: CHART --- */')

print("=== EXACT ORIGINAL SLIDE 3 STATIONS CSS FROM HEAD ===")
print(head[pos_start:pos_end])
