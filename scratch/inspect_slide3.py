import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect slide-data-feeds HTML
pos = text.find('id="slide-data-feeds"')
print("=== SLIDE DATA FEEDS HTML ===")
print(text[pos:pos+2500].encode('ascii', errors='replace').decode('ascii'))

# Let's find CSS rules for feed-card in index.html
style = re.search(r'<style>([\s\S]*?)</style>', text).group(1)
print("\n=== CSS FOR FEED CARDS IN INDEX.HTML ===")
for b in re.split(r'\}', style):
    if any(k in b for k in ['.feed-card', '.feed-status', '.feed-name', '.feed-detail', '.feeds-grid', '.online', '.syncing']):
        print(b.strip() + '}\n')
