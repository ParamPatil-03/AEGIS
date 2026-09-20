with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    head = f.read()

# Let's search for "slide-2" in head
pos_s2 = head.find('id="slide-2"')
end_s2 = head.find('class="slide', pos_s2 + 20)
print("=== SLIDE-2 (FORECAST / STATIONS) IN HEAD ===")
print(head[pos_s2:end_s2][:3000].encode('ascii', errors='replace').decode('ascii'))
