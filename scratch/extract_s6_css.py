with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's see CSS rules for #slide-5 and .s6-
import re
css_matches = re.findall(r'(\.(?:s6-|pipeline-|stage-|inspector-|formula-|meth-|data-sources|source-)[a-zA-Z0-9_-]*\s*\{[^}]+\})', text)
print(f"Found {len(css_matches)} relevant CSS rules:")
for m in css_matches:
    print("---")
    print(m.strip())
