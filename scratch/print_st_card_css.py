with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('.st-card {')
print(text[pos-200:pos+1600].encode('ascii', errors='replace').decode('ascii'))
