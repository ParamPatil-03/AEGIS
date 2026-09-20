import re

with open('api.py', 'r', encoding='utf-8') as f:
    text = f.read()

for m in re.finditer(r'@app\.(get|post|websocket)\([\'"]([^\'"]+)', text):
    print(m.group(1), m.group(2))
