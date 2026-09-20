with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's find window.addEventListener('DOMContentLoaded' or 'load' or initial fetch
pos = text.find("DOMContentLoaded")
if pos != -1:
    print("Found DOMContentLoaded at:", pos)
    print(text[pos:pos+1500])
else:
    print("DOMContentLoaded not found!")
    # look for window.onload
    pos2 = text.find("window.onload")
    if pos2 != -1:
        print("Found window.onload at:", pos2)
        print(text[pos2:pos2+1000])
