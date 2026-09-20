import os
import glob
import time

files = glob.glob('scratch/*')
for f in sorted(files, key=os.path.getmtime):
    mtime = os.path.getmtime(f)
    t_str = time.strftime('%H:%M:%S', time.localtime(mtime))
    if '11:' in t_str or '12:' in t_str or '13:' in t_str:
        print(f"{t_str} - {f}")
