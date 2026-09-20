with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('val-lucknow-1h')
slide_start = text.rfind('<div class="slide', 0, pos)
print('Slide containing val-lucknow-1h:')
print(text[slide_start:slide_start+100])
