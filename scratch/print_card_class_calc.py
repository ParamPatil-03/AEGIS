with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = 443007
print(text[pos-800:pos].encode('ascii', errors='replace').decode('ascii'))
