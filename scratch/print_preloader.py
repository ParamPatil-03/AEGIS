with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('class="preloader"')
print("Found preloader at:", pos)
if pos != -1:
    print(text[pos-40:pos+800].encode('ascii', errors='replace').decode('ascii'))
