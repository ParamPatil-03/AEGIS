with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = 424181
print(text[pos+2500:pos+3500].encode('ascii', errors='replace').decode('ascii'))
