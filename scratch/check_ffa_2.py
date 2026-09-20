with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("function fetchForecastAll")
print(text[pos+1400:pos+2800].encode('ascii', errors='replace').decode('ascii'))
