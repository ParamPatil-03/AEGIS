with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = 432420
print(text[pos-1000:pos].encode('ascii', errors='replace').decode('ascii'))
