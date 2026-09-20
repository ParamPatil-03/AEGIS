import re

with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    head = f.read()

with open('index.html', 'r', encoding='utf-8') as f:
    curr = f.read()

# What features were added into curr that were NOT in head?
# Let's check:
# 1. CME simulation (prompt 4)
print("CME simulation in curr:", "0C. 3D CME Simulation" in curr)

# 2. Smooth scrolling / GSAP changes?
head_scroll = re.search(r'// --- (?:Scroll|Navigation|GSAP)[\s\S]*?(?=// ---|\Z)', head)
curr_scroll = re.search(r'// --- (?:Scroll|Navigation|GSAP)[\s\S]*?(?=// ---|\Z)', curr)

# 3. Slide 8 structure changes?
head_s8 = re.search(r'<div class=["\']slide\b[^"\']*["\']\s+id=["\']slide-5["\'][\s\S]*?(?=<div class=["\']slide|\Z)', head)
curr_s8 = re.search(r'<div class=["\']slide\b[^"\']*["\']\s+id=["\']slide-5["\'][\s\S]*?(?=<div class=["\']slide|\Z)', curr)

print("Head S8 length:", len(head_s8.group(0)) if head_s8 else "None")
print("Curr S8 length:", len(curr_s8.group(0)) if curr_s8 else "None")

# 4. Slide 9 (slide-6)
head_s9 = re.search(r'<div class=["\']slide\b[^"\']*["\']\s+id=["\']slide-6["\'][\s\S]*?(?=<div class=["\']slide|\Z)', head)
curr_s9 = re.search(r'<div class=["\']slide\b[^"\']*["\']\s+id=["\']slide-6["\'][\s\S]*?(?=<div class=["\']slide|\Z)', curr)

print("Head S9 length:", len(head_s9.group(0)) if head_s9 else "None")
print("Curr S9 length:", len(curr_s9.group(0)) if curr_s9 else "None")
