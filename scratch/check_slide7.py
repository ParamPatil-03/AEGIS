with open('index.html', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'id="slide-4"' in line:
        print(f"Found on line {i+1}")
        start = max(0, i - 10)
        end = min(len(lines), i + 150)
        for j in range(start, end):
            print(f"{j+1}: {lines[j]}", end='')
        break
