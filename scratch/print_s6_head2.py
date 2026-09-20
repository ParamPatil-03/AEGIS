with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    head = f.read()

pos = head.find('id="slide-6"')
print(head[pos+1500:pos+3000].encode('ascii', errors='replace').decode('ascii'))
