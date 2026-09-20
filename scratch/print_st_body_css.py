with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('.st-body {')
print(text[pos:pos+1500].encode('ascii', errors='replace').decode('ascii'))
