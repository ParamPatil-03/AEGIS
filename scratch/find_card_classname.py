with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("card.className = 'st-card'")
print('Found card.className at:', pos)
print(text[pos-400:pos+300].encode('ascii', errors='replace').decode('ascii'))
