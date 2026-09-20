with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('id="slide-5"')
end_pos = text.find('id="slide-6"')
slide_html = text[pos:end_pos]
print("Length of Slide 8 HTML:", len(slide_html))
print("--- FIRST 1500 CHARS ---")
print(slide_html[:1500].encode('ascii', errors='replace').decode('ascii'))
print("--- NEXT 1500 CHARS ---")
print(slide_html[1500:3000].encode('ascii', errors='replace').decode('ascii'))
