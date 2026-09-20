import re

with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    head = f.read()

with open('index.html', 'r', encoding='utf-8') as f:
    curr = f.read()

def get_slide0_rules(html):
    style = re.search(r'<style>([\s\S]*?)</style>', html).group(1)
    # Find all selectors mentioning slide-0 or inside slide-0
    terms = ['slide-0', 'hero', 'massive-text', 'flare-graphic', 'badge', 'glitch', 'sub-hero']
    rules = []
    for block in re.split(r'\}', style):
        if any(t in block for t in terms):
            rules.append(block.strip() + '}')
    return '\n'.join(rules)

print("=== HEAD SLIDE 0 RULES ===")
print(get_slide0_rules(head))

print("\n=== CURR SLIDE 0 RULES ===")
print(get_slide0_rules(curr))
