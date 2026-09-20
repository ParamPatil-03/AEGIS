with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = 424181
print(text[pos+1000:pos+2500].encode('ascii', errors='replace').decode('ascii'))
