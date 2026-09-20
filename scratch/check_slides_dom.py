from bs4 import BeautifulSoup
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
slides = soup.find_all(class_='slide')

for s in slides:
    sid = s.get('id')
    # Count elements, text length
    text_len = len(s.get_text(strip=True))
    all_tags = len(s.find_all())
    print(f"Slide id='{sid}': text_len={text_len}, total_dom_nodes={all_tags}")
