from bs4 import BeautifulSoup

with open('index.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

slide = soup.find(id='slide-data-feeds')
if slide:
    ids = [el.get('id') for el in slide.find_all(id=True)]
    print("IDs in slide-data-feeds:", ids)
else:
    print("slide-data-feeds NOT FOUND!")
