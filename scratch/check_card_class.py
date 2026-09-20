with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("const range =")
print(text[pos:pos+1000].encode('ascii', errors='replace').decode('ascii'))
