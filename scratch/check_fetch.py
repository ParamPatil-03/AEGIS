import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

funcs = ['fetchStatus', 'fetchForecastAll', 'updateChart', 'fetchInsights', 'fetchImpact', 'fetchMethodology', 'initTelemetryWebSocket']
for fn in funcs:
    match = re.search(r'(async\s+)?function\s+' + fn + r'\b.*?\{', text)
    if match:
        start = match.start()
        # print first 500 chars of function
        print(f"=== {fn} ===")
        print(text[start:start+600])
        print("...\n")
