with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("setCard('feed-xray'")
outer_func_pos = text.rfind('function ', 0, text.rfind('function ', 0, pos))
print('Outer function signature:', text[outer_func_pos:outer_func_pos+80])
