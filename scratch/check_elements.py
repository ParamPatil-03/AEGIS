import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Find all element IDs
all_ids = set(re.findall(r'id=["\']([^"\']+)["\']', text))
print(f"Total element IDs: {len(all_ids)}")

# Find all IDs referenced in javascript
js_part = text[text.find('<script>'):] if '<script>' in text else text
referenced_ids = set(re.findall(r'getElementById\(["\']([^"\']+)["\']\)', js_part))
print(f"Total referenced IDs in JS: {len(referenced_ids)}")

missing_in_html = [i for i in referenced_ids if i not in all_ids]
print(f"Referenced in JS but missing in HTML: {missing_in_html}")

# Check placeholder texts
placeholders = re.findall(r'<span[^>]*id=["\']([^"\']+)["\'][^>]*>\s*([—\-]+)\s*</span>', text)
print(f"Span placeholders with dashes: {placeholders[:25]}")
