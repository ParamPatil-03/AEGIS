with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    head_lines = f.readlines()
with open('index.html', 'r', encoding='utf-8') as f:
    curr_lines = f.readlines()

import difflib
diff = list(difflib.unified_diff(head_lines, curr_lines, fromfile='HEAD', tofile='CURR', n=1))

print(f"Total diff lines: {len(diff)}")
# Let's see what parts were modified
chunks = []
cur_chunk = []
for line in diff:
    if line.startswith('@@'):
        if cur_chunk:
            chunks.append(cur_chunk)
        cur_chunk = [line]
    elif cur_chunk:
        cur_chunk.append(line)
if cur_chunk:
    chunks.append(cur_chunk)

print(f"Number of modified chunks: {len(chunks)}")
for i, c in enumerate(chunks):
    header = c[0]
    sample = [l for l in c[1:] if l.startswith('+') or l.startswith('-')][:6]
    print(f"\n--- Chunk {i+1}: {header} ---")
    print(''.join(sample))
