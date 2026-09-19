import re
import os
import json

def audit_html():
    print("=== AUDITING index.html ===")
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Check for script tag balance
    open_scripts = len(re.findall(r"<script\b", html, re.I))
    close_scripts = len(re.findall(r"</script>", html, re.I))
    print(f"Script tags: <script>: {open_scripts}, </script>: {close_scripts}")

    # Check for unclosed divs or tags
    open_divs = len(re.findall(r"<div\b", html, re.I))
    close_divs = len(re.findall(r"</div>", html, re.I))
    print(f"Div tags: <div>: {open_divs}, </div>: {close_divs}")

    # Check getElementById
    ids_in_js = re.findall(r"getElementById\(['\"]([^'\"]+)['\"]\)", html)
    unique_js_ids = sorted(list(set(ids_in_js)))
    ids_in_html = set(re.findall(r'id=["\']([^"\']+)["\']', html))

    missing = [i for i in unique_js_ids if i not in ids_in_html]
    print(f"Total getElementById: {len(ids_in_js)}, Unique: {len(unique_js_ids)}")
    print(f"Missing DOM IDs referenced by getElementById ({len(missing)}):")
    for m in missing:
        print(f"  - {m}")

    # Check onclick handlers
    onclicks = re.findall(r'onclick=["\']([^"\']+)["\']', html)
    functions_called = set()
    for oc in onclicks:
        # extract function names
        m = re.match(r'([a-zA-Z0-9_]+)\(', oc.strip())
        if m:
            functions_called.add(m.group(1))

    # Find functions declared in JS
    js_funcs = set(re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', html))
    js_const_funcs = set(re.findall(r'(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*(?:function|\([^)]*\)\s*=>)', html))
    all_declared_funcs = js_funcs | js_const_funcs

    missing_funcs = [fn for fn in functions_called if fn not in all_declared_funcs]
    print(f"\nMissing JS functions called in HTML onclick ({len(missing_funcs)}):")
    for fn in missing_funcs:
        print(f"  - {fn}")

    # Check fetch URLs
    fetches = re.findall(r'fetch\([`\'"]([^`\'"]+)[`\'"]', html)
    print(f"\nFetches in index.html ({len(fetches)}):")
    for url in sorted(set(fetches)):
        print(f"  - {url}")

if __name__ == '__main__':
    audit_html()
