with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("setCard('feed-xray'")
print('Found setCard at:', pos)
func_pos = text.rfind('function ', 0, pos)
print('Function signature:', text[func_pos:func_pos+60])
print('Lines around function start:')
print(text[func_pos:func_pos+300])
