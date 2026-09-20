with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("// Default Feed Cards")
print(text[pos:pos+800].encode('ascii', errors='replace').decode('ascii'))
