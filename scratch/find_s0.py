with open('index.html', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'id="slide-0"' in line or "id='slide-0'" in line:
        print(f"Slide 0 HTML at line {i+1}:")
        for j in range(max(0, i-5), min(len(lines), i+40)):
            print(f"{j+1}: {lines[j].rstrip()}")
        break

for i, line in enumerate(lines):
    if '/* --- SLIDE 1: INTRO / LANDING --- */' in line:
        print(f"\nSlide 1 CSS at line {i+1}:")
        for j in range(i, min(len(lines), i+80)):
            print(f"{j+1}: {lines[j].rstrip()}")
            if '/* --- SLIDE 2' in lines[j]:
                break
        break
