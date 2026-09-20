with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('id="slide-5"')
end_pos = text.find('id="slide-6"')
slide_html = text[pos:end_pos]

import re
# Find top-level children inside s6-container
s6_pos = slide_html.find('class="s6-container"')
print("Found s6-container at:", s6_pos)

# Let's see what is inside s6-col-right and what is below s6-main-grid
mg_pos = slide_html.find('class="s6-main-grid"')
end_mg = slide_html.find('<!-- Data Sources Ribbon Strip -->')
print("Found Data Sources Ribbon Strip at:", end_mg)
if end_mg != -1:
    print("--- CONTENT AFTER MAIN GRID ---")
    print(slide_html[end_mg:end_mg+800].encode('ascii', errors='replace').decode('ascii'))
