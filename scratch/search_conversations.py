import json
import os

conv_dirs = [
    r'C:\Users\PARAM\.gemini\antigravity-ide\brain\4c1a25ef-b317-47bc-96d6-069d66777932\.system_generated\logs\transcript.jsonl',
    r'C:\Users\PARAM\.gemini\antigravity-ide\brain\514cfeaf-231a-465a-aa39-7672634bb767\.system_generated\logs\transcript.jsonl'
]

for p in conv_dirs:
    if not os.path.exists(p): continue
    print(f"=== READING {p} ===")
    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            try:
                d = json.loads(line)
            except:
                continue
            if d.get('type') == 'USER_INPUT':
                c = d.get('content', '')
                if any(w in c.lower() for w in ['slide', 'color', 'block', 'theme', 'yellow', 'gold']):
                    print("USER:", c.strip().replace('\n', ' ')[:150])
            elif d.get('type') == 'PLANNER_RESPONSE':
                c = d.get('content', '')
                # if assistant mentioned slide 3 or colored blocks
                if 'slide 3' in str(c).lower() or 'st-card' in str(c).lower() or 'whole block' in str(c).lower():
                    print("ASSISTANT (brief):", str(c).strip().replace('\n', ' ')[:150])
