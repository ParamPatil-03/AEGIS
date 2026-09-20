with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("function updateDataFeedsSlide")
if pos == -1: pos = text.find("setCard('feed-xray'")
print("Found at:", pos)
if pos != -1:
    print(text[pos-200:pos+1200].encode('ascii', errors='replace').decode('ascii'))
