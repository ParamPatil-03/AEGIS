with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("function applyImmediateHydration")
print("Found applyImmediateHydration at:", pos)
if pos != -1:
    print(text[pos:pos+1500])
