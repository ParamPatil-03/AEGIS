import re

with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    head = f.read()

with open('index.html', 'r', encoding='utf-8') as f:
    curr = f.read()

# Let's extract slide-data-feeds in both
m_head = re.search(r'(<div class=["\']slide\b[^"\']*["\']\s+id=["\']slide-data-feeds["\'][\s\S]*?)(?=<div class=["\']slide|\Z)', head)
m_curr = re.search(r'(<div class=["\']slide\b[^"\']*["\']\s+id=["\']slide-data-feeds["\'][\s\S]*?)(?=<div class=["\']slide|\Z)', curr)

# Also let's find CSS rules mentioning data-feeds, feed-card, feed-badge, feed-status, etc.
def get_feed_css(html):
    style = re.search(r'<style>([\s\S]*?)</style>', html).group(1)
    rules = []
    for b in re.split(r'\}', style):
        if any(k in b.lower() for k in ['feed', 'slide-data-feeds', 'badge-live', 'pulse-green', 'pulse-yellow']):
            rules.append(b.strip() + '}')
    return '\n'.join(rules)

print("=== HEAD CSS FOR DATA FEEDS ===")
print(get_feed_css(head)[:2000])

print("\n=== CURR CSS FOR DATA FEEDS ===")
print(get_feed_css(curr)[:2000])
