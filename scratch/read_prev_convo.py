import json

with open(r'C:\Users\PARAM\.gemini\antigravity-ide\brain\514cfeaf-231a-465a-aa39-7672634bb767\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get('type') == 'USER_INPUT':
            print("USER_INPUT:")
            print(data.get('content'))
