import re

with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    head = f.read()
with open('index.html', 'r', encoding='utf-8') as f:
    curr = f.read()

head_style = re.search(r'<style>([\s\S]*?)</style>', head).group(1)
curr_style = re.search(r'<style>([\s\S]*?)</style>', curr).group(1)

print("=== HEAD BODY FONT & STYLES ===")
for line in head_style.splitlines()[:50]:
    if any(k in line for k in ['font', 'color', '--', 'body', 'massive', 'h1', 'flare']):
        print(line)

print("\n=== CURR BODY FONT & STYLES ===")
for line in curr_style.splitlines()[:50]:
    if any(k in line for k in ['font', 'color', '--', 'body', 'massive', 'h1', 'flare']):
        print(line)

print("\n=== SLIDE 0 IN HEAD STYLE ===")
for m in re.finditer(r'(\.massive-text[\s\S]*?\})', head_style):
    print("HEAD:", m.group(1))

print("\n=== SLIDE 0 IN CURR STYLE ===")
for m in re.finditer(r'(\.massive-text[\s\S]*?\})', curr_style):
    print("CURR:", m.group(1))

print("\n=== FLARE GRAPHIC IN HEAD STYLE ===")
for m in re.finditer(r'(\.flare-graphic[\s\S]*?\})', head_style):
    print("HEAD:", m.group(1))

print("\n=== FLARE GRAPHIC IN CURR STYLE ===")
for m in re.finditer(r'(\.flare-graphic[\s\S]*?\})', curr_style):
    print("CURR:", m.group(1))
