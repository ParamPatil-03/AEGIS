import re

with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    head = f.read()

with open('index.html', 'r', encoding='utf-8') as f:
    curr = f.read()

def inspect_slide(html, slide_id):
    pos = html.find(f'id="{slide_id}"')
    if pos == -1: return ""
    next_pos = html.find('class="slide', pos + 20)
    if next_pos == -1: next_pos = pos + 3000
    return html[pos:next_pos]

print("=== HEAD SLIDE-1 (TELEMETRY) ===")
s1_h = inspect_slide(head, 'slide-1')
print(s1_h[:800].encode('ascii', errors='replace').decode('ascii'))

print("\n=== HEAD SLIDE-DATA-FEEDS (DATA FEEDS) ===")
sdf_h = inspect_slide(head, 'slide-data-feeds')
print(sdf_h[:800].encode('ascii', errors='replace').decode('ascii'))

print("\n=== HEAD SLIDE-2 (FORECAST) ===")
s2_h = inspect_slide(head, 'slide-2')
print(s2_h[:800].encode('ascii', errors='replace').decode('ascii'))
