with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('.st-card')
print('Found .st-card at:', pos)
if pos != -1:
    print(text[pos-100:pos+800].encode('ascii', errors='replace').decode('ascii'))
