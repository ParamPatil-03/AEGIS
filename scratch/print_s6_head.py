with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    head = f.read()

pos = head.find('id="slide-6"')
print("Found id=slide-6 at:", pos)
print(head[pos:pos+1500].encode('ascii', errors='replace').decode('ascii'))
