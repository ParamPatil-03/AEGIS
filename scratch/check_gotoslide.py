with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("function goToSlide")
print(text[pos:pos+1500])
