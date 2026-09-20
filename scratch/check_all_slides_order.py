import re
from bs4 import BeautifulSoup

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
slides = soup.find_all(class_='slide')
print(f"Total slides: {len(slides)}")
for i, s in enumerate(slides):
    sid = s.get('id', 'no-id')
    h = s.find(['h1', 'h2', 'h3'])
    htext = h.get_text(strip=True) if h else ''
    label = s.find(class_='cyan-label')
    ltext = label.get_text(strip=True) if label else ''
    badge = s.find(class_='stage-num-badge')
    btext = badge.get_text(strip=True) if badge else ''
    print(f"Slide index {i} | 1-based #{i+1} | id={sid} | label='{ltext}' | h='{htext}' | badge='{btext}'")
