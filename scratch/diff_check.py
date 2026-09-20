import difflib
import re

with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    head = f.read()
with open('index.html', 'r', encoding='utf-8') as f:
    curr = f.read()

# Let's inspect :root styles
head_root = re.search(r':root\s*\{[^}]+\}', head)
curr_root = re.search(r':root\s*\{[^}]+\}', curr)

print("--- HEAD :root ---")
if head_root: print(head_root.group(0))

print("\n--- CURR :root ---")
if curr_root: print(curr_root.group(0))

# Let's inspect slide-0 in both
head_s1_match = re.search(r'(<section[^>]*id=["\']slide-0["\'][\s\S]*?</section>)', head)
curr_s1_match = re.search(r'(<section[^>]*id=["\']slide-0["\'][\s\S]*?</section>)', curr)

print("\n--- SLIDE 0 DIFF ---")
if head_s1_match and curr_s1_match:
    h_lines = head_s1_match.group(1).splitlines()
    c_lines = curr_s1_match.group(1).splitlines()
    diff = list(difflib.unified_diff(h_lines, c_lines, lineterm=''))
    print('\n'.join(diff[:60]))
