import urllib.request

res = urllib.request.urlopen('http://127.0.0.1:8000')
print('Status:', res.status)
content = res.read().decode('utf-8')
print('Has preloader:', 'id="preloader"' in content)
print('Has Haval font:', 'Haval' in content)
print('Has massive-text scale:', 'clamp(3.2rem, 9.5vw, 8.5rem)' in content)
print('Has radiant yellow outline:', '-webkit-text-stroke: 2.5px #FFB800' in content)
print('Has full flare:', 'width: 48vw;' in content)
