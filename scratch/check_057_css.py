with open('scratch/commit_057b3f7.html', 'r', encoding='utf-8', errors='ignore') as f:
    text_057 = f.read()

import re
css_m = re.search(r'<style>([\s\S]*?)</style>', text_057)
if css_m:
    css = css_m.group(1)
    for r in re.findall(r'([^{}]*\{[^{}]*\})', css):
        if any(c in r for c in ['#', 'rgb', 'var(--accent']):
            # Print selector and background/color
            lines = [l.strip() for l in r.split('\n') if any(w in l for w in ['background', 'color:', 'border:'])]
            sel = r.split('{')[0].strip().replace('\n', ' ')
            if any('background' in l for l in lines):
                print(sel, "-->", lines)
