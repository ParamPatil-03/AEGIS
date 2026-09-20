with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("function applyLiveTelemetryData")
print("Found applyLiveTelemetryData at:", pos)
if pos != -1:
    print(text[pos:pos+1200].encode('ascii', errors='replace').decode('ascii'))
