with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("Multi-station forecast baseline values")
print(text[pos:pos+1200].encode('ascii', errors='replace').decode('ascii'))
