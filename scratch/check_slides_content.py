from bs4 import BeautifulSoup

with open('index.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

slider = soup.find(id='slider-container')
slides = slider.find_all(class_='slide', recursive=False)

for i, s in enumerate(slides):
    slide_id = s.get('id', 'no-id')
    # Count elements
    cards = len(s.find_all(class_=lambda c: c and ('card' in c or 'grid' in c or 'col' in c)))
    headings = [h.get_text(strip=True) for h in s.find_all(['h1', 'h2', 'h3'])]
    print(f"Slide {i} (ID: {slide_id}): Headings: {headings[:2]}, Internal containers: {cards}")
