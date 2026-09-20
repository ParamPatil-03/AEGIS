with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('id="slide-5"')
end_pos = text.find('id="slide-6"')
slide_html = text[pos:end_pos]

# Print last 2000 chars of slide_html
print(slide_html[-2000:].encode('ascii', errors='replace').decode('ascii'))
