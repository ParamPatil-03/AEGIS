import re

with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    head = f.read()

with open('index.html', 'r', encoding='utf-8') as f:
    curr = f.read()

# Let's see differences in slide-data-feeds
pos_h = head.find('id="slide-data-feeds"')
end_h = head.find('class="slide', pos_h + 30)
pos_c = curr.find('id="slide-data-feeds"')
end_c = curr.find('class="slide', pos_c + 30)

print("=== SLIDE-DATA-FEEDS HEAD ===")
print(head[pos_h:end_h].encode('ascii', errors='replace').decode('ascii'))

print("\n=== SLIDE-DATA-FEEDS CURR ===")
print(curr[pos_c:end_c].encode('ascii', errors='replace').decode('ascii'))
