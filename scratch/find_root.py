with open('api.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "@app.get('/')" in l or '@app.get("/")' in l:
        print(f"Line {i+1}: {l.strip()}")
        for j in range(i, min(len(lines), i + 25)):
            print(f"{j+1}: {lines[j].strip()}")
