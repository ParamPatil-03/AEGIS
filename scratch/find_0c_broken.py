with open('scratch/broken_theme_index.html', 'r', encoding='utf-8') as f:
    broken = f.read()

pos = broken.find('0C. 3D CME Simulation')
if pos != -1:
    print("Found 0C. 3D CME Simulation at:", pos)
    print(broken[pos:pos+500])
else:
    print("0C. 3D CME Simulation NOT found in broken_theme_index.html")
