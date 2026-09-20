import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

orig_len = len(content)
print(f"Original index.html length: {orig_len} chars")

# 1. Add @font-face declarations at the beginning of <style>
font_faces = """        /* Parallel Universe Typography (Haval & Bounded) */
        @font-face {
            font-family: 'Haval';
            src: url('fonts/Haval-Regular.woff2') format('woff2');
            font-weight: 400;
            font-style: normal;
            font-display: swap;
        }
        @font-face {
            font-family: 'Haval';
            src: url('fonts/Haval-Medium.woff2') format('woff2');
            font-weight: 500;
            font-style: normal;
            font-display: swap;
        }
        @font-face {
            font-family: 'Haval';
            src: url('fonts/Haval-Light.woff2') format('woff2');
            font-weight: 300;
            font-style: normal;
            font-display: swap;
        }
        @font-face {
            font-family: 'Bounded';
            src: url('fonts/Bounded-Variable.ttf') format('truetype');
            font-weight: 100 900;
            font-style: normal;
            font-display: swap;
        }

"""

# Insert font faces right after <style>
content = content.replace('<style>\n', f'<style>\n{font_faces}', 1)

# 2. Update :root variables
old_root_pattern = r':root\s*\{[^}]+\}'
new_root = """:root {
            /* Parallel Universe Luxury Theme: Pitch Black, Antique Champagne Gold, Radiant Solar Yellow, Celestial Blue & Pure White */
            --bg: #0A0B0E;
            --panel: #111318;
            --fg: #E1D9C1;
            --fg-white: #FFFFFF;
            --fg-muted: #A39B8B;
            --accent-gold: #E1D9C1;
            --accent-gold-dark: #C5A059;
            --accent-gold-antique: #D4AF37;
            --accent-yellow: #FFB800;
            --accent-amber: #F59E0B;
            --accent-cyan: #E5A93C; /* Radiant solar gold / amber (maps legacy cyan to glowing gold) */
            --accent-purple: #D4AF37; /* Antique metallic gold (maps legacy purple to rich gold) */
            --accent-blue: #3B82F6; /* Cosmic electric blue */
            --accent-white: #FFFFFF; /* High-contrast white */
            --grid-color: rgba(225, 217, 193, 0.05);
            --border-heavy: 2px solid var(--accent-gold);
            --border-subtle: 1px solid rgba(225, 217, 193, 0.18);
        }"""

content = re.sub(old_root_pattern, new_root, content, count=1)

# 3. Update body, html font-family
content = content.replace(
    "font-family: 'Space Mono', monospace;\n            overflow: hidden !important;",
    "font-family: 'Bounded', 'Space Mono', sans-serif;\n            letter-spacing: -0.16px;\n            overflow: hidden !important;"
)

# 4. Update h1, h2, h3 font-family
content = content.replace(
    "h1,\n        h2,\n        h3 {\n            font-family: 'Syne', sans-serif;\n            text-transform: uppercase;\n            line-height: 0.85;\n            margin: 0;\n        }",
    "h1,\n        h2,\n        h3,\n        h4 {\n            font-family: 'Haval', 'Syne', sans-serif;\n            text-transform: uppercase;\n            letter-spacing: 0.02em;\n            color: var(--accent-gold);\n            line-height: 0.9;\n            margin: 0;\n        }"
)

# 5. Side HUD styling
content = content.replace(
    "background: rgba(11, 14, 23, 0.95);",
    "background: rgba(10, 11, 14, 0.96);"
)
content = content.replace(
    "border-right: 2px solid rgba(255, 255, 255, 0.1);",
    "border-right: 2px solid rgba(225, 217, 193, 0.12);"
)
content = content.replace(
    ".side-logo {\n            font-family: 'Syne', sans-serif;\n            font-weight: 800;\n            font-size: 1.5rem;\n            color: var(--accent-cyan);\n            writing-mode: vertical-rl;\n            transform: rotate(180deg);\n            letter-spacing: 2px;\n            text-shadow: 2px 2px 0px var(--accent-purple);\n        }",
    ".side-logo {\n            font-family: 'Haval', 'Syne', sans-serif;\n            font-weight: 500;\n            font-size: 1.6rem;\n            color: var(--accent-gold);\n            writing-mode: vertical-rl;\n            transform: rotate(180deg);\n            letter-spacing: 3px;\n            text-shadow: 2px 2px 0px rgba(212, 175, 55, 0.5);\n        }"
)

# Side link hover and active styling
content = content.replace(
    "font-family: 'Syne', sans-serif;\n            font-weight: 800;\n            font-size: 1.2rem;\n            letter-spacing: 1px;\n            opacity: 0;\n            visibility: hidden;\n            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);\n            pointer-events: none;\n            white-space: nowrap;\n            box-shadow: 4px 4px 0px var(--accent-purple);",
    "font-family: 'Haval', 'Syne', sans-serif;\n            font-weight: 500;\n            font-size: 1.15rem;\n            letter-spacing: 1.5px;\n            opacity: 0;\n            visibility: hidden;\n            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);\n            pointer-events: none;\n            white-space: nowrap;\n            background: var(--accent-gold);\n            color: #0A0B0E;\n            box-shadow: 4px 4px 0px #C5A059;"
)

content = content.replace(
    ".side-link.active span {\n            color: var(--accent-cyan);\n            text-shadow: 0 0 10px var(--accent-cyan);\n        }",
    ".side-link.active span {\n            color: var(--accent-yellow);\n            text-shadow: 0 0 10px rgba(255, 184, 0, 0.7);\n        }"
)

content = content.replace(
    ".side-link.active::before {\n            content: '';\n            position: absolute;\n            left: 0;\n            top: 50%;\n            transform: translateY(-50%);\n            width: 4px;\n            height: 40px;\n            background: var(--accent-cyan);\n            box-shadow: 0 0 10px var(--accent-cyan);\n        }",
    ".side-link.active::before {\n            content: '';\n            position: absolute;\n            left: 0;\n            top: 50%;\n            transform: translateY(-50%);\n            width: 4px;\n            height: 40px;\n            background: var(--accent-yellow);\n            box-shadow: 0 0 10px rgba(255, 184, 0, 0.8);\n        }"
)

content = content.replace(
    ".radar-spin {\n            width: 100%;\n            height: 100%;\n            border: 2px dashed var(--accent-purple);",
    ".radar-spin {\n            width: 100%;\n            height: 100%;\n            border: 2px dashed var(--accent-yellow);"
)

content = content.replace(
    "background: var(--accent-purple);\n            transform: translate(-50%, -50%);\n            border-radius: 50%;",
    "background: var(--accent-gold);\n            transform: translate(-50%, -50%);\n            border-radius: 50%;"
)

content = content.replace(
    ".side-audio-btn {\n            width: 36px;\n            height: 36px;\n            border: 1px solid rgba(255, 255, 255, 0.2);\n            background: rgba(11, 14, 23, 0.9);\n            color: var(--accent-cyan);",
    ".side-audio-btn {\n            width: 36px;\n            height: 36px;\n            border: 1px solid rgba(225, 217, 193, 0.25);\n            background: rgba(17, 19, 24, 0.9);\n            color: var(--accent-gold);"
)

content = content.replace(
    ".side-audio-btn:hover {\n            border-color: var(--accent-cyan);\n            box-shadow: 0 0 10px rgba(0, 229, 255, 0.4);",
    ".side-audio-btn:hover {\n            border-color: var(--accent-yellow);\n            box-shadow: 0 0 10px rgba(255, 184, 0, 0.4);"
)

# 6. Hero Slide text
content = content.replace(
    ".massive-text {\n            font-size: clamp(2.5rem, 8vw, 8rem);\n            font-weight: 800;\n            letter-spacing: -0.05em;\n            color: var(--fg);\n            /* Solid, sharp offset shadow - NO BLUR, NO RGBA */\n            text-shadow: 4px 4px 0px var(--accent-purple);\n        }",
    ".massive-text {\n            font-family: 'Haval', 'Syne', sans-serif;\n            font-size: clamp(2.5rem, 8vw, 8rem);\n            font-weight: 800;\n            letter-spacing: -0.03em;\n            color: var(--fg-white);\n            text-shadow: 4px 4px 0px #8C6D37;\n        }"
)

content = content.replace(
    "-webkit-text-stroke: 2px var(--accent-cyan);",
    "-webkit-text-stroke: 2px var(--accent-yellow);"
)

content = content.replace(
    ".s1-sub {\n            margin-top: 1.5rem;\n            font-size: 1rem;\n            max-width: 600px;\n            text-transform: uppercase;\n            border-left: 4px solid var(--accent-cyan);\n            padding-left: 1rem;\n            background: rgba(11, 14, 23, 0.7);\n        }",
    ".s1-sub {\n            font-family: 'Bounded', sans-serif;\n            margin-top: 1.5rem;\n            font-size: 1.05rem;\n            max-width: 620px;\n            text-transform: uppercase;\n            border-left: 4px solid var(--accent-yellow);\n            padding-left: 1.2rem;\n            background: rgba(10, 11, 14, 0.85);\n            color: var(--fg);\n            letter-spacing: 0.5px;\n            line-height: 1.6;\n        }"
)

content = content.replace(
    "background: radial-gradient(circle, var(--accent-cyan) 0%, transparent 60%);",
    "background: radial-gradient(circle, #E5A93C 0%, rgba(255, 184, 0, 0.15) 45%, transparent 70%);"
)

# 7. Slide 2: Telemetry
content = content.replace(
    ".s2-title-box {\n            padding: 2rem;\n            border-bottom: var(--border-heavy);\n            background: var(--fg);\n            color: var(--bg);\n            flex: 0 0 auto;\n        }",
    ".s2-title-box {\n            padding: 2rem;\n            border-bottom: var(--border-heavy);\n            background: var(--accent-gold);\n            color: #0A0B0E;\n            flex: 0 0 auto;\n        }"
)

content = content.replace(
    ".s2-title-box h2 {\n            font-size: 2.5rem;\n            letter-spacing: -1px;\n        }",
    ".s2-title-box h2 {\n            font-family: 'Haval', 'Syne', sans-serif;\n            font-size: 2.5rem;\n            letter-spacing: 0.5px;\n            color: #0A0B0E;\n        }"
)

content = content.replace(
    ".data-val {\n            font-family: 'Syne', sans-serif;\n            font-size: 3rem;\n            font-weight: 800;\n            color: var(--accent-cyan);\n        }",
    ".data-val {\n            font-family: 'Haval', 'Syne', sans-serif;\n            font-size: 3rem;\n            font-weight: 800;\n            color: var(--accent-gold);\n        }"
)

# 8. Preloader Theme
old_preloader_bg = """        .preloader {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: #07090F;
            background: radial-gradient(circle at 50% 50%, #15122e 0%, #0c1120 45%, #07090F 85%);"""

new_preloader_bg = """        .preloader {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: #08090C;
            background: radial-gradient(circle at 50% 50%, #161820 0%, #0d0f14 45%, #08090C 85%);"""

content = content.replace(old_preloader_bg, new_preloader_bg)

content = content.replace(
    "linear-gradient(rgba(0, 229, 255, 0.05) 1px, transparent 1px),\n                linear-gradient(90deg, rgba(139, 92, 246, 0.05) 1px, transparent 1px);",
    "linear-gradient(rgba(225, 217, 193, 0.06) 1px, transparent 1px),\n                linear-gradient(90deg, rgba(255, 184, 0, 0.05) 1px, transparent 1px);"
)

content = content.replace(
    "background: radial-gradient(circle, rgba(0, 229, 255, 0.18) 0%, rgba(139, 92, 246, 0.1) 40%, transparent 70%);",
    "background: radial-gradient(circle, rgba(255, 184, 0, 0.22) 0%, rgba(212, 175, 55, 0.12) 40%, transparent 70%);"
)

content = content.replace(
    "border: 1.5px solid rgba(0, 229, 255, 0.7);\n            border-radius: 50%;\n            pointer-events: none;\n            opacity: 0;\n            box-shadow: 0 0 25px rgba(0, 229, 255, 0.5), inset 0 0 15px rgba(139, 92, 246, 0.4);",
    "border: 1.5px solid rgba(255, 184, 0, 0.8);\n            border-radius: 50%;\n            pointer-events: none;\n            opacity: 0;\n            box-shadow: 0 0 25px rgba(255, 184, 0, 0.5), inset 0 0 15px rgba(212, 175, 55, 0.4);"
)

content = content.replace(
    "filter: drop-shadow(0 0 30px rgba(0, 229, 255, 0.35)) drop-shadow(4px 4px 0px rgba(139, 92, 246, 0.8));",
    "filter: drop-shadow(0 0 30px rgba(255, 184, 0, 0.35)) drop-shadow(4px 4px 0px rgba(212, 175, 55, 0.6));"
)

content = content.replace(
    "background: linear-gradient(90deg, var(--accent-cyan, #00E5FF), var(--accent-purple, #8B5CF6));\n            box-shadow: 0 0 10px var(--accent-cyan, #00E5FF);",
    "background: linear-gradient(90deg, #FFB800, #E1D9C1, #D4AF37);\n            box-shadow: 0 0 10px rgba(255, 184, 0, 0.6);"
)

# Update Preloader SVG Gradients
old_svg_grads = """                    <!-- Electric Cyan to Purple Neon Gradient -->
                    <linearGradient id="aegisStroke" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="#00E5FF"/>
                        <stop offset="25%" stop-color="#38BDF8"/>
                        <stop offset="65%" stop-color="#818CF8"/>
                        <stop offset="100%" stop-color="#C084FC"/>
                    </linearGradient>

                    <!-- Metallic Pearl to Lilac Fill Gradient -->
                    <linearGradient id="aegisFill" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#FFFFFF"/>
                        <stop offset="35%" stop-color="#E0F7FA"/>
                        <stop offset="70%" stop-color="#EDE9FE"/>
                        <stop offset="100%" stop-color="#DDD6FE"/>
                    </linearGradient>"""

new_svg_grads = """                    <!-- Radiant Solar Gold to Antique Champagne Stroke Gradient -->
                    <linearGradient id="aegisStroke" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="#FFB800"/>
                        <stop offset="30%" stop-color="#E1D9C1"/>
                        <stop offset="70%" stop-color="#D4AF37"/>
                        <stop offset="100%" stop-color="#FFFFFF"/>
                    </linearGradient>

                    <!-- Luxury Pure White to Champagne Ivory Fill Gradient -->
                    <linearGradient id="aegisFill" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#FFFFFF"/>
                        <stop offset="35%" stop-color="#F4EFE0"/>
                        <stop offset="70%" stop-color="#E1D9C1"/>
                        <stop offset="100%" stop-color="#C5A059"/>
                    </linearGradient>"""

content = content.replace(old_svg_grads, new_svg_grads)

# 9. Chart Controls & Buttons
content = content.replace(
    ".ctrl-btn.active {\n            background: var(--accent-cyan);\n            color: #0B0E17;\n            border-color: var(--accent-cyan);",
    ".ctrl-btn.active {\n            background: var(--accent-gold);\n            color: #0A0B0E;\n            border-color: var(--accent-gold);"
)
content = content.replace(
    ".replay-select {\n            background: #0B0E17;\n            color: var(--accent-cyan);",
    ".replay-select {\n            background: #111318;\n            color: var(--accent-gold);"
)

# 10. Chart.js colors in JS
old_chart_js = """                // Visual emphasis for the currently selected forecast horizon point
                const activeIdx = focusedHorizon === '1h' ? 1 : (focusedHorizon === '3h' ? 2 : 3);
                const pRadii   = [5, 5, 5, 5];
                const pBg      = ['#888', '#8B5CF6', '#8B5CF6', '#8B5CF6'];
                const pBorder  = ['#888', '#8B5CF6', '#8B5CF6', '#8B5CF6'];
                const pBWidth  = [1, 1, 1, 1];

                pRadii[activeIdx]  = 9;
                pBg[activeIdx]     = '#00E5FF';
                pBorder[activeIdx] = '#FFFFFF';
                pBWidth[activeIdx] = 3;

                datasets = [
                    {
                        label: `AEGIS FORECAST (${focusedMetric.toUpperCase()})`,
                        data: predSeries,
                        borderColor: '#8B5CF6',
                        borderWidth: 3.5,
                        pointRadius: pRadii,
                        pointBackgroundColor: pBg,
                        pointBorderColor: pBorder,
                        pointBorderWidth: pBWidth,
                        tension: 0.25
                    },
                    {
                        label: `95% CONFORMAL UPPER BOUND`,
                        data: upperBand,
                        borderColor: 'rgba(234, 179, 8, 0.75)',
                        borderWidth: 1.5,
                        borderDash: [4, 4],
                        pointRadius: 3,
                        fill: false
                    },
                    {
                        label: `95% CONFORMAL LOWER BOUND`,
                        data: lowerBand,
                        borderColor: 'rgba(234, 179, 8, 0.75)',
                        borderWidth: 1.5,
                        borderDash: [4, 4],
                        pointRadius: 3,
                        fill: '-1',
                        backgroundColor: 'rgba(234, 179, 8, 0.10)'
                    }
                ];"""

new_chart_js = """                // Visual emphasis for the currently selected forecast horizon point (Parallel Universe Gold Theme)
                const activeIdx = focusedHorizon === '1h' ? 1 : (focusedHorizon === '3h' ? 2 : 3);
                const pRadii   = [5, 5, 5, 5];
                const pBg      = ['#888', '#D4AF37', '#D4AF37', '#D4AF37'];
                const pBorder  = ['#888', '#D4AF37', '#D4AF37', '#D4AF37'];
                const pBWidth  = [1, 1, 1, 1];

                pRadii[activeIdx]  = 9;
                pBg[activeIdx]     = '#FFB800';
                pBorder[activeIdx] = '#FFFFFF';
                pBWidth[activeIdx] = 3;

                datasets = [
                    {
                        label: `AEGIS FORECAST (${focusedMetric.toUpperCase()})`,
                        data: predSeries,
                        borderColor: '#FFB800',
                        borderWidth: 3.5,
                        pointRadius: pRadii,
                        pointBackgroundColor: pBg,
                        pointBorderColor: pBorder,
                        pointBorderWidth: pBWidth,
                        tension: 0.25
                    },
                    {
                        label: `95% CONFORMAL UPPER BOUND`,
                        data: upperBand,
                        borderColor: 'rgba(225, 217, 193, 0.75)',
                        borderWidth: 1.5,
                        borderDash: [4, 4],
                        pointRadius: 3,
                        fill: false
                    },
                    {
                        label: `95% CONFORMAL LOWER BOUND`,
                        data: lowerBand,
                        borderColor: 'rgba(225, 217, 193, 0.75)',
                        borderWidth: 1.5,
                        borderDash: [4, 4],
                        pointRadius: 3,
                        fill: '-1',
                        backgroundColor: 'rgba(255, 184, 0, 0.12)'
                    }
                ];"""

content = content.replace(old_chart_js, new_chart_js)

# Update chart tooltip and default styling
content = content.replace(
    "backgroundColor: '#F3F4F6',\n                            titleColor: '#0B0E17',\n                            bodyColor: '#8B5CF6',",
    "backgroundColor: '#111318',\n                            titleColor: '#E1D9C1',\n                            bodyColor: '#FFB800',\n                            borderColor: 'rgba(225, 217, 193, 0.3)',\n                            borderWidth: 1,"
)
content = content.replace(
    "titleFont: { size: 13, family: \"'Syne', sans-serif\" },",
    "titleFont: { size: 13, family: \"'Haval', 'Syne', sans-serif\" },"
)
content = content.replace(
    "grid: { color: 'rgba(255,255,255,0.08)', tickLength: 6 },",
    "grid: { color: 'rgba(225, 217, 193, 0.06)', tickLength: 6 },"
)
content = content.replace(
    "grid: { color: 'rgba(255,255,255,0.08)' },",
    "grid: { color: 'rgba(225, 217, 193, 0.06)' },"
)

# 11. CME Simulation Timeline & HUD
content = content.replace(
    "background: linear-gradient(90deg, rgba(255, 140, 0, 0.4), rgba(0, 229, 255, 0.4), rgba(139, 92, 246, 0.4));",
    "background: linear-gradient(90deg, rgba(255, 184, 0, 0.6), rgba(225, 217, 193, 0.6), rgba(59, 130, 246, 0.6));"
)
content = content.replace(
    ".cme-phase-label {\n            font-family: 'Space Mono', monospace;\n            font-size: 0.65rem;\n            font-weight: 700;\n            letter-spacing: 0.15em;\n            padding: 4px 10px;\n            background: rgba(0, 229, 255, 0.12);\n            color: var(--accent-cyan);\n            border: 1px solid rgba(0, 229, 255, 0.35);",
    ".cme-phase-label {\n            font-family: 'Bounded', 'Space Mono', monospace;\n            font-size: 0.68rem;\n            font-weight: 700;\n            letter-spacing: 0.15em;\n            padding: 4px 12px;\n            background: rgba(225, 217, 193, 0.12);\n            color: var(--accent-gold);\n            border: 1px solid rgba(225, 217, 193, 0.35);"
)
content = content.replace(
    ".cme-tl-phase.active {\n            color: var(--accent-cyan);\n            font-weight: 700;\n            border-left-color: var(--accent-cyan);\n        }",
    ".cme-tl-phase.active {\n            color: var(--accent-yellow);\n            font-weight: 700;\n            border-left-color: var(--accent-yellow);\n        }"
)

# 12. Leaflet and popup dark theme
content = content.replace(
    "background: #0B0E17 !important;\n            font-family: 'Space Mono', monospace;",
    "background: #0A0B0E !important;\n            font-family: 'Bounded', 'Space Mono', monospace;"
)
content = content.replace(
    ".leaflet-popup-content-wrapper {\n            background: #0d1117;\n            border: 1px solid rgba(0,229,255,0.4);",
    ".leaflet-popup-content-wrapper {\n            background: #111318;\n            border: 1px solid rgba(225, 217, 193, 0.35);"
)

# 13. SHAP table bar gradient replacements
content = content.replace(
    ".shap-bar-fill.pos {\n            background: linear-gradient(90deg, rgba(139, 92, 246, 0.4), #8B5CF6);\n            box-shadow: 0 0 8px rgba(139, 92, 246, 0.5);\n        }",
    ".shap-bar-fill.pos {\n            background: linear-gradient(90deg, rgba(212, 175, 55, 0.4), #D4AF37);\n            box-shadow: 0 0 8px rgba(212, 175, 55, 0.5);\n        }"
)
content = content.replace(
    ".shap-bar-fill.neg {\n            background: linear-gradient(90deg, rgba(0, 229, 255, 0.4), #00E5FF);\n            box-shadow: 0 0 8px rgba(0, 229, 255, 0.5);\n        }",
    ".shap-bar-fill.neg {\n            background: linear-gradient(90deg, rgba(255, 184, 0, 0.4), #FFB800);\n            box-shadow: 0 0 8px rgba(255, 184, 0, 0.5);\n        }"
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Updated index.html: {len(content)} chars (delta: {len(content) - orig_len})")
