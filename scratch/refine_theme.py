import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

orig_len = len(content)

# 1. Update font-family: 'Syne', sans-serif -> 'Haval', 'Syne', sans-serif
content = re.sub(r"font-family:\s*'Syne',\s*sans-serif", "font-family: 'Haval', 'Syne', sans-serif", content)

# 2. In JS, replace legacy color strings
content = content.replace("alertElem.style.color = '#00E5FF';", "alertElem.style.color = 'var(--accent-cyan)';")
content = content.replace("liveBadge.style.color = '#00E5FF';", "liveBadge.style.color = 'var(--accent-cyan)';")
content = content.replace("warnbarTag.style.color = '#00E5FF';", "warnbarTag.style.color = 'var(--accent-yellow)';")
content = content.replace("warnbarTag.style.borderColor = '#00E5FF';", "warnbarTag.style.borderColor = 'var(--accent-yellow)';")

# 3. In Replay Chart.js
content = content.replace(
    "borderColor: '#00E5FF',\n                            borderWidth: 2.5,",
    "borderColor: '#3B82F6',\n                            borderWidth: 2.5,"
)
content = content.replace(
    "borderColor: '#8B5CF6',\n                            borderWidth: 2.5,\n                            borderDash: [6, 6],",
    "borderColor: '#FFB800',\n                            borderWidth: 2.5,\n                            borderDash: [6, 6],"
)
content = content.replace(
    "borderColor: '#00E5FF',\n                            borderWidth: 3,\n                            stepped: true",
    "borderColor: '#3B82F6',\n                            borderWidth: 3,\n                            stepped: true"
)
content = content.replace(
    "borderColor: '#8B5CF6',\n                            borderWidth: 3,\n                            borderDash: [8, 8],\n                            stepped: true",
    "borderColor: '#FFB800',\n                            borderWidth: 3,\n                            borderDash: [8, 8],\n                            stepped: true"
)

# 4. In CSS, replace remaining #0B0E17 with #0A0B0E
content = content.replace("background: #0B0E17 !important;", "background: #0A0B0E !important;")
content = content.replace("color: #0B0E17 !important;", "color: #0A0B0E !important;")
content = content.replace("background: #0B0E17;", "background: #111318;")
content = content.replace("color: #0B0E17;", "color: #0A0B0E;")
content = content.replace("badge.style.color = '#0B0E17';", "badge.style.color = '#0A0B0E';")

# 5. Slide 4 / Slide 7 Operational Impact nominal theme
content = content.replace(
    "#slide-4.theme-nominal {\n            background: #0A0B0E !important;\n            color: #F3F4F6 !important;\n        }",
    "#slide-4.theme-nominal {\n            background: #0A0B0E !important;\n            color: #E1D9C1 !important;\n        }"
)

# 6. Make sure all card borders have subtle luxury gold styling
content = content.replace(
    "border: 1px solid rgba(255, 255, 255, 0.15);",
    "border: 1px solid rgba(225, 217, 193, 0.18);"
)
content = content.replace(
    "border: 1px solid rgba(255,255,255,0.15);",
    "border: 1px solid rgba(225, 217, 193, 0.18);"
)
content = content.replace(
    "border-bottom: 1px solid rgba(255, 255, 255, 0.15);",
    "border-bottom: 1px solid rgba(225, 217, 193, 0.15);"
)
content = content.replace(
    "border-top: 1px solid rgba(255,255,255,0.1);",
    "border-top: 1px solid rgba(225, 217, 193, 0.15);"
)
content = content.replace(
    "border-top:1px solid rgba(255,255,255,0.1)",
    "border-top:1px solid rgba(225, 217, 193, 0.15)"
)

# 7. Write back
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Refined index.html: {len(content)} chars (delta: {len(content) - orig_len})")
