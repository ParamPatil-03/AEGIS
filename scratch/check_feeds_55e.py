import subprocess
import re

out = subprocess.check_output(['git', 'show', '55e5970:index.html'], text=True, encoding='utf-8', errors='replace')

# Find slide-data-feeds in 55e5970
pos = out.find('id="slide-data-feeds"')
end = out.find('class="slide', pos + 30)
print("=== SLIDE-DATA-FEEDS in 55e5970 ===")
print(out[pos:end])

# Find all CSS related to feeds in 55e5970
style = re.search(r'<style>([\s\S]*?)</style>', out).group(1)
print("\n=== CSS FOR FEEDS in 55e5970 ===")
for b in re.split(r'\}', style):
    if any(k in b for k in ['.feed-', '.feeds-', 'slide-data-feeds']):
        print(b.strip() + '}\n')
