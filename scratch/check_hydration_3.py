with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("function applyImmediateHydration")
print(text[pos+2000:pos+3500].encode('ascii', errors='replace').decode('ascii'))
