import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

orig_len = len(content)

# 1. Replace the CSS block for Slide 8
old_css_start = content.find('/* --- SLIDE 8: METHODOLOGY & ARCHITECTURE --- */')
old_css_end = content.find('/* --- SLIDE 7: STATION MAP --- */')

new_css = """/* --- SLIDE 8: METHODOLOGY & ARCHITECTURE (Anti-Overlap Flexbox Optimization) --- */
        .s6-container {
            display: flex;
            flex-direction: column;
            width: 100%;
            height: 100%;
            max-width: 1400px;
            margin: 0 auto;
            min-height: 0;
            overflow: hidden;
            gap: 0.5rem;
            padding-bottom: 0.5rem;
        }

        .s6-top-hud {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(225, 217, 193, 0.18);
            padding-bottom: 0.4rem;
            margin-bottom: 0.1rem;
            font-family: 'Space Mono', monospace;
            flex-shrink: 0;
            flex-wrap: wrap;
            gap: 10px;
        }

        .meth-badge-live {
            font-size: 0.68rem;
            font-weight: 700;
            padding: 2px 8px;
            border: 1px solid var(--accent-gold);
            background: rgba(225, 217, 193, 0.12);
            color: var(--accent-gold);
            letter-spacing: 0.5px;
        }

        .s6-main-grid {
            display: grid;
            grid-template-columns: 42% 58%;
            gap: 1.25rem;
            align-items: stretch;
            flex: 1;
            min-height: 0;
            overflow: hidden;
        }

        .s6-col-left {
            display: flex;
            flex-direction: column;
            min-height: 0;
            gap: 0.5rem;
            overflow: hidden;
        }

        .s6-col-left-header {
            flex-shrink: 0;
        }

        .pipeline-stages-list {
            display: flex;
            flex-direction: column;
            gap: 0.45rem;
            flex: 1;
            min-height: 0;
            overflow-y: auto;
            padding-right: 4px;
        }

        .pipeline-stages-list::-webkit-scrollbar,
        .inspector-content-scroll::-webkit-scrollbar,
        .table-scroll-container::-webkit-scrollbar,
        .eia-pillars-list::-webkit-scrollbar {
            width: 4px;
        }

        .pipeline-stages-list::-webkit-scrollbar-thumb,
        .inspector-content-scroll::-webkit-scrollbar-thumb,
        .table-scroll-container::-webkit-scrollbar-thumb,
        .eia-pillars-list::-webkit-scrollbar-thumb {
            background: rgba(225, 217, 193, 0.3);
            border-radius: 2px;
        }

        .pipeline-stage-card {
            border: 1px solid rgba(225, 217, 193, 0.18);
            border-left: 3px solid rgba(225, 217, 193, 0.35);
            background: rgba(17, 19, 24, 0.7);
            padding: 0.55rem 0.85rem;
            font-family: 'Bounded', 'Space Mono', monospace;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            flex-shrink: 0;
        }

        .pipeline-stage-card:hover {
            transform: translateX(3px);
            background: rgba(225, 217, 193, 0.05);
            border-color: rgba(225, 217, 193, 0.4);
        }

        .pipeline-stage-card.selected {
            border-left: 3px solid var(--accent-yellow) !important;
            border-color: rgba(255, 184, 0, 0.45) !important;
            background: rgba(255, 184, 0, 0.06) !important;
            box-shadow: 0 4px 15px rgba(255, 184, 0, 0.12);
        }

        .stage-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.2rem;
        }

        .stage-num-badge {
            font-size: 0.62rem;
            font-weight: 800;
            padding: 1px 5px;
            background: rgba(225, 217, 193, 0.15);
            color: var(--accent-gold);
            letter-spacing: 0.5px;
        }

        .stage-status-badge {
            font-size: 0.6rem;
            font-weight: 700;
            color: #10B981;
            letter-spacing: 0.5px;
        }

        .stage-card-title {
            font-family: 'Haval', 'Syne', sans-serif;
            font-size: 0.95rem;
            font-weight: 700;
            color: #F8F9FA;
            letter-spacing: 0.5px;
            margin-bottom: 2px;
        }

        .stage-card-sub {
            font-size: 0.66rem;
            opacity: 0.75;
            margin: 1px 0 4px 0;
            line-height: 1.25;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .stage-card-footer {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        }

        .stage-meta-tag {
            font-size: 0.58rem;
            padding: 1px 5px;
            border: 1px solid rgba(225, 217, 193, 0.2);
            background: rgba(0, 0, 0, 0.35);
            opacity: 0.85;
            color: var(--accent-gold);
        }

        .s6-col-right {
            display: flex;
            flex-direction: column;
            min-height: 0;
            gap: 0.5rem;
            overflow: hidden;
        }

        .meth-panel {
            display: flex;
            flex-direction: column;
            flex: 1;
            min-height: 0;
            overflow: hidden;
        }

        .inspector-card {
            border: 1px solid rgba(225, 217, 193, 0.18);
            background: rgba(17, 19, 24, 0.85);
            padding: 0.8rem 1.1rem;
            font-family: 'Bounded', 'Space Mono', monospace;
            height: 100%;
            display: flex;
            flex-direction: column;
            min-height: 0;
            overflow: hidden;
        }

        .inspector-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 1px solid rgba(225, 217, 193, 0.12);
            padding-bottom: 0.4rem;
            margin-bottom: 0.4rem;
            gap: 0.8rem;
            flex-shrink: 0;
        }

        .inspector-title {
            font-family: 'Haval', 'Syne', sans-serif;
            font-size: 1.2rem;
            font-weight: 700;
            margin: 2px 0 1px 0;
            color: var(--accent-gold);
        }

        .inspector-subtitle {
            font-size: 0.7rem;
            color: var(--accent-yellow);
        }

        .insp-status-badge {
            font-size: 0.62rem;
            font-weight: 700;
            padding: 2px 6px;
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid #10B981;
            color: #10B981;
            white-space: nowrap;
        }

        .inspector-content-scroll {
            flex: 1;
            min-height: 0;
            overflow-y: auto;
            padding-right: 4px;
            display: flex;
            flex-direction: column;
            gap: 0.45rem;
        }

        .inspector-summary {
            font-size: 0.75rem;
            line-height: 1.35;
            color: rgba(225, 217, 193, 0.9);
        }

        .formula-box {
            background: rgba(0, 0, 0, 0.5);
            border: 1px dashed rgba(225, 217, 193, 0.35);
            padding: 0.4rem 0.7rem;
            flex-shrink: 0;
        }

        .formula-label {
            font-size: 0.58rem;
            color: var(--accent-yellow);
            font-weight: 700;
            letter-spacing: 0.5px;
            margin-bottom: 2px;
        }

        .formula-code {
            font-size: 0.72rem;
            color: #F8F9FA;
            font-family: 'Bounded', 'Space Mono', monospace;
            word-break: break-all;
        }

        .research-bullets {
            font-size: 0.72rem;
            line-height: 1.4;
            color: rgba(225, 217, 193, 0.85);
            padding-left: 1.1rem;
        }

        .inspector-tech-footer {
            flex-shrink: 0;
            padding-top: 0.4rem;
            border-top: 1px solid rgba(225, 217, 193, 0.1);
            margin-top: auto;
        }

        .tech-stack-row {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
        }

        .tech-chip {
            font-size: 0.6rem;
            font-weight: 700;
            padding: 2px 6px;
            background: rgba(225, 217, 193, 0.08);
            border: 1px solid rgba(225, 217, 193, 0.25);
            color: var(--accent-gold);
        }

        .table-scroll-container {
            flex: 1;
            overflow-y: auto;
            border: 1px solid rgba(225, 217, 193, 0.15);
            background: rgba(0, 0, 0, 0.25);
            margin-bottom: 0.4rem;
            min-height: 0;
        }

        .benchmark-table {
            width: 100%;
            border-collapse: collapse;
            font-family: 'Bounded', 'Space Mono', monospace;
            font-size: 0.72rem;
            text-align: left;
        }

        .benchmark-table th {
            padding: 5px 7px;
            background: rgba(225, 217, 193, 0.08);
            border-bottom: 2px solid rgba(225, 217, 193, 0.25);
            color: var(--accent-gold);
            font-weight: 800;
            font-size: 0.66rem;
            position: sticky;
            top: 0;
        }

        .benchmark-table td {
            padding: 4px 7px;
            border-bottom: 1px solid rgba(225, 217, 193, 0.06);
        }

        .benchmark-table tr:hover td {
            background: rgba(225, 217, 193, 0.05);
        }

        .benchmark-audit-note {
            font-size: 0.65rem;
            line-height: 1.3;
            color: rgba(225, 217, 193, 0.75);
            padding: 0.4rem;
            background: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.3);
            flex-shrink: 0;
        }

        .eia-pillars-list {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            flex: 1;
            overflow-y: auto;
            min-height: 0;
        }

        .eia-pillar-box {
            border: 1px solid rgba(225, 217, 193, 0.12);
            background: rgba(255, 255, 255, 0.02);
            padding: 0.6rem 0.8rem;
            border-left: 3px solid var(--accent-gold);
            flex-shrink: 0;
        }

        .eia-pillar-title {
            font-weight: 800;
            font-size: 0.76rem;
            color: var(--accent-gold);
            margin-bottom: 2px;
            letter-spacing: 0.5px;
        }

        .eia-pillar-text {
            font-size: 0.7rem;
            line-height: 1.35;
            color: rgba(225, 217, 193, 0.85);
        }

        .data-sources-strip {
            border: 1px solid rgba(225, 217, 193, 0.18);
            background: rgba(17, 19, 24, 0.85);
            padding: 0.45rem 0.8rem;
            flex-shrink: 0;
        }

        .data-sources-grid {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 0.35rem;
        }

        .source-tag {
            background: rgba(225, 217, 193, 0.06);
            border: 1px solid rgba(225, 217, 193, 0.2);
            color: var(--accent-gold);
            font-size: 0.62rem;
            font-weight: 700;
            padding: 0.3rem 0.2rem;
            text-align: center;
            font-family: 'Bounded', 'Space Mono', monospace;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .source-tag:hover {
            background: rgba(255, 184, 0, 0.15);
            border-color: var(--accent-yellow);
            color: var(--accent-yellow);
        }

        .source-tag.active {
            background: var(--accent-gold) !important;
            color: #0A0B0E !important;
            font-weight: 800 !important;
            border-color: var(--accent-gold) !important;
        }

        .source-detail-drawer {
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(225, 217, 193, 0.12);
            padding: 0.35rem 0.6rem;
            margin-top: 0.35rem;
            font-family: 'Bounded', 'Space Mono', monospace;
        }
        
        """

content = content[:old_css_start] + new_css + content[old_css_end:]

# 2. Update HTML of Slide 8 (#slide-5)
old_html_pattern = r'<div class="slide" id="slide-5">.*?<!-- SLIDE 7: STATION MAP -->'

new_html = """<div class="slide" id="slide-5">
            <div class="s6-container">
                <!-- Top HUD Row -->
                <div class="s6-top-hud">
                    <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
                        <span class="cyan-label" style="margin:0; font-size:0.85rem; color:var(--accent-yellow);">STAGE 08 METHODOLOGY &amp; ARCHITECTURE</span>
                        <span id="meth-status-chip" class="meth-badge-live">● 12 ENSEMBLE MODELS LOADED // CPU INFERENCE: 3.2ms</span>
                    </div>

                    <!-- Mode / Tab Controls -->
                    <div class="ctrl-group">
                        <span class="ctrl-label">INSPECTION VIEW:</span>
                        <div class="btn-group" id="meth-tab-btns">
                            <button class="ctrl-btn active" id="btn-meth-stages" onclick="setMethodologyTab('stages')">PIPELINE AUDIT</button>
                            <button class="ctrl-btn" id="btn-meth-benchmarks" onclick="setMethodologyTab('benchmarks')">BENCHMARKS (R &gt; 0.98)</button>
                            <button class="ctrl-btn" id="btn-meth-eia" onclick="setMethodologyTab('eia')">WHY INDIA? (EIA)</button>
                        </div>
                    </div>
                </div>

                <!-- Main 2-Column Grid -->
                <div class="s6-main-grid">
                    <!-- Left Column: Pipeline Stages List -->
                    <div class="s6-col-left">
                        <div class="s6-col-left-header">
                            <div class="cyan-label" style="margin-bottom:0.15rem; font-size:0.75rem;">OPERATIONAL ARCHITECTURE</div>
                            <h2 class="offset-heading" style="font-size:1.85rem; margin-bottom:0.25rem;">HOW AEGIS WORKS</h2>
                            <div style="font-family:'Bounded', 'Space Mono', monospace; font-size:0.68rem; color:rgba(225,217,193,0.7);">
                                Click any pipeline stage below to audit its math, data flows, and active technology stack:
                            </div>
                        </div>

                        <div class="pipeline-stages-list" id="meth-stages-container">
                            <div class="pipeline-stage-card selected" onclick="selectMethodologyStage('acquisition')" id="stage-card-acquisition">
                                <div class="stage-card-header">
                                    <span class="stage-num-badge">STAGE 01</span>
                                    <span class="stage-status-badge">ONLINE</span>
                                </div>
                                <div class="stage-card-title">DATA ACQUISITION</div>
                                <div class="stage-card-sub">NOAA GOES · NASA OMNIWeb · GFZ Potsdam · NASA CDDIS RINEX</div>
                                <div class="stage-card-footer">
                                    <span class="stage-meta-tag">&lt; 60s INGEST CYCLE</span>
                                    <span class="stage-meta-tag">72H ROLLING BUFFER</span>
                                </div>
                            </div>

                            <div class="pipeline-stage-card" onclick="selectMethodologyStage('features')" id="stage-card-features">
                                <div class="stage-card-header">
                                    <span class="stage-num-badge">STAGE 02</span>
                                    <span class="stage-status-badge">ACTIVE</span>
                                </div>
                                <div class="stage-card-title">FEATURE ENGINEERING</div>
                                <div class="stage-card-sub">48 Physics-Informed Vectors · 1h/3h/6h Lags · ΔTEC Derivatives</div>
                                <div class="stage-card-footer">
                                    <span class="stage-meta-tag">&lt; 1.2ms TRANSFORM</span>
                                    <span class="stage-meta-tag">DIURNAL HARMONICS</span>
                                </div>
                            </div>

                            <div class="pipeline-stage-card" onclick="selectMethodologyStage('inference')" id="stage-card-inference">
                                <div class="stage-card-header">
                                    <span class="stage-num-badge">STAGE 03</span>
                                    <span class="stage-status-badge">OPERATIONAL</span>
                                </div>
                                <div class="stage-card-title">DUAL-LAYER INFERENCE</div>
                                <div class="stage-card-sub">XGBoost 2.0 Regressors + Bidirectional LSTM + TreeSHAP</div>
                                <div class="stage-card-footer">
                                    <span class="stage-meta-tag">12 LOADED MODELS</span>
                                    <span class="stage-meta-tag">3.2ms CPU INFERENCE</span>
                                </div>
                            </div>

                            <div class="pipeline-stage-card" onclick="selectMethodologyStage('warning')" id="stage-card-warning">
                                <div class="stage-card-header">
                                    <span class="stage-num-badge">STAGE 04</span>
                                    <span class="stage-status-badge">CALIBRATED</span>
                                </div>
                                <div class="stage-card-title">CONFORMAL WARNING ENGINE</div>
                                <div class="stage-card-sub">95% Empirical Safety Bounds · GAGAN APV-I &amp; NavIC Holdover</div>
                                <div class="stage-card-footer">
                                    <span class="stage-meta-tag">NON-PARAMETRIC</span>
                                    <span class="stage-meta-tag">1–6h LEAD TIME</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Right Column: Interactive Detail Display -->
                    <div class="s6-col-right">
                        <!-- Panel 1: Stage Deep-Dive Inspector -->
                        <div class="meth-panel active" id="meth-panel-stages">
                            <div class="inspector-card">
                                <div class="inspector-header">
                                    <div>
                                        <span class="stage-num-badge" id="insp-stage-num">STAGE 01</span>
                                        <h3 class="inspector-title" id="insp-stage-title">DATA ACQUISITION</h3>
                                        <div class="inspector-subtitle" id="insp-stage-sub">Multi-Source Heterogeneous Ingestion</div>
                                    </div>
                                    <div style="text-align:right;">
                                        <span class="insp-status-badge" id="insp-stage-status">ONLINE // LIVE STREAMING</span>
                                        <div style="font-size:0.65rem; font-family:'Space Mono', monospace; opacity:0.75; margin-top:3px;" id="insp-stage-latency">&lt; 60s ingest cycle</div>
                                    </div>
                                </div>

                                <div class="inspector-content-scroll">
                                    <div class="inspector-summary" id="insp-stage-summary">
                                        Continuous telemetry ingestion from spaceborne solar monitors and ground-based dual-frequency GNSS networks across India and Sri Lanka.
                                    </div>

                                    <!-- Mathematical Formulation Box -->
                                    <div class="formula-box" id="insp-formula-box">
                                        <div class="formula-label">MATHEMATICAL DERIVATION / GOVERNING EQUATION:</div>
                                        <div class="formula-code" id="insp-stage-formula">VTEC = α · [ (f₁² · f₂²) / (f₁² - f₂²) ] · (P₂ - P₁)</div>
                                    </div>

                                    <!-- Technical Details List -->
                                    <ul class="research-bullets" id="insp-stage-bullets" style="gap:0.4rem; margin-top:0.3rem; margin-bottom:0.3rem;">
                                        <li>Solar &amp; Interplanetary: Real-time NOAA GOES-16 0.1-0.8nm X-ray flux, NASA OMNIWeb IMF Bz, solar wind velocity (Vsw), proton density, and GFZ Potsdam Kp indices.</li>
                                        <li>Ground GNSS Network: 30-second dual-frequency RINEX carrier-phase observations from IGS/NASA CDDIS stations (Hyderabad, Bangalore, Lucknow, Colombo).</li>
                                        <li>Sliding Ingestion Buffer: 72-hour rolling telemetry window with automated anomaly detection and out-of-bounds rejection.</li>
                                    </ul>
                                </div>

                                <!-- Tech Stack Chips Footer -->
                                <div class="inspector-tech-footer">
                                    <div class="cyan-label" style="font-size:0.65rem; margin-bottom:0.25rem;">ACTIVE TECHNOLOGY STACK:</div>
                                    <div class="tech-stack-row" id="insp-tech-stack">
                                        <span class="tech-chip">NOAA SWPC REST</span>
                                        <span class="tech-chip">NASA CDAWeb</span>
                                        <span class="tech-chip">GFZ Potsdam API</span>
                                        <span class="tech-chip">NASA CDDIS RINEX</span>
                                        <span class="tech-chip">Python AsyncIO</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Panel 2: Verified Model Benchmarks Table -->
                        <div class="meth-panel" id="meth-panel-benchmarks" style="display:none;">
                            <div class="inspector-card">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem; flex-wrap:wrap; gap:8px; flex-shrink:0;">
                                    <div>
                                        <h3 style="font-family: 'Haval', 'Syne', sans-serif; font-size:1.15rem; margin:0; font-weight:700; color:var(--accent-gold);">
                                            STAGE 5 ENSEMBLE TEST BENCHMARK
                                        </h3>
                                        <div style="font-family:'Space Mono', monospace; font-size:0.65rem; opacity:0.75;">
                                            INDEPENDENT 2023–2024 TEST SET (3,867 HOURS · INCLUDING MARCH 2023 G4 STORM)
                                        </div>
                                    </div>
                                    <div class="btn-group" id="benchmark-filter-btns">
                                        <button class="ctrl-btn active" onclick="filterBenchmarks('ALL')">ALL</button>
                                        <button class="ctrl-btn" onclick="filterBenchmarks('1H')">1H</button>
                                        <button class="ctrl-btn" onclick="filterBenchmarks('3H')">3H</button>
                                        <button class="ctrl-btn" onclick="filterBenchmarks('6H')">6H</button>
                                    </div>
                                </div>

                                <div class="table-scroll-container">
                                    <table class="benchmark-table">
                                        <thead>
                                            <tr>
                                                <th>STATION</th>
                                                <th>HORIZON</th>
                                                <th>RMSE (TECU)</th>
                                                <th>MAE</th>
                                                <th>PEARSON R</th>
                                                <th>CALM 95% COV</th>
                                                <th>STORM COV</th>
                                            </tr>
                                        </thead>
                                        <tbody id="benchmark-table-body">
                                            <!-- Dynamically populated from /api/methodology -->
                                        </tbody>
                                    </table>
                                </div>

                                <div class="benchmark-audit-note">
                                    <span style="color:var(--accent-yellow); font-weight:bold;">⚠️ OPERATIONAL DIAGNOSTIC AUDIT:</span>
                                    Conformal coverage maintains nominal &gt;94.5% during calm periods. Under severe geomagnetic storm forcing (Kp ≥ 5), empirical storm coverage compresses, confirming that AEGIS conformal prediction requires dynamic storm inflation.
                                </div>
                            </div>
                        </div>

                        <!-- Panel 3: Why India? EIA Physics -->
                        <div class="meth-panel" id="meth-panel-eia" style="display:none;">
                            <div class="inspector-card">
                                <div style="flex-shrink:0; margin-bottom:0.4rem;">
                                    <h3 style="font-family: 'Haval', 'Syne', sans-serif; font-size:1.15rem; font-weight:700; margin:0 0 0.2rem 0; color:var(--accent-gold);">
                                        WHY INDIA? // EQUATORIAL IONIZATION ANOMALY
                                    </h3>
                                    <div style="font-family:'Space Mono', monospace; font-size:0.65rem; color:rgba(225,217,193,0.7);">
                                        REGIONAL GEOMAGNETIC ADVANTAGE &amp; LOW-LATITUDE IONOSPHERIC VULNERABILITY
                                    </div>
                                </div>

                                <div class="eia-pillars-list" id="eia-pillars-container">
                                    <div class="eia-pillar-box">
                                        <div class="eia-pillar-title">1. EIA FOUNTAIN EFFECT DYNAMICS</div>
                                        <div class="eia-pillar-text">
                                            The magnetic dip equator passes directly south of India (Trivandrum/Colombo). Daytime eastward electric fields produce the fountain effect (E×B vertical plasma drift), lifting ionospheric plasma to 800+ km altitude which subsequently diffuses down geomagnetic field lines onto northern crests (Hyderabad and Lucknow), generating intense TEC gradients and plasma bubbles.
                                        </div>
                                    </div>
                                    <div class="eia-pillar-box">
                                        <div class="eia-pillar-title">2. INDIGENOUS SATELLITE CONSTELLATIONS (GAGAN &amp; NAVIC)</div>
                                        <div class="eia-pillar-text">
                                            India's civil aviation augmentation system (ISRO GAGAN) and NavIC regional satellite fleet operate directly within this low-latitude EIA belt. Global space-weather models (trained on European and North American mid-latitudes) consistently underestimate steep equatorial TEC gradients.
                                        </div>
                                    </div>
                                    <div class="eia-pillar-box">
                                        <div class="eia-pillar-title">3. TRANSECT GROUND NETWORK (EQUATOR TO CREST APEX)</div>
                                        <div class="eia-pillar-text">
                                            AEGIS bridges the full latitudinal transect: Colombo (equatorial source baseline, 6.89°N) → Bangalore (sub-equatorial transition, 13.02°N) → Hyderabad (southern crest flank, 17.42°N) → Lucknow (northern EIA crest apex, 26.91°N).
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Bottom Data Sources Strip -->
                        <div class="data-sources-strip">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.25rem;">
                                <div class="cyan-label" style="font-size:0.65rem; margin:0; color:var(--accent-yellow);">ACTIVE INGESTION DATA FEEDS (CLICK TO AUDIT PROVENANCE):</div>
                                <div id="source-agency-chip" style="font-family:'Space Mono', monospace; font-size:0.62rem; color:var(--accent-gold);">● NOAA SWPC LIVE</div>
                            </div>
                            <div class="data-sources-grid" id="data-sources-grid">
                                <div class="source-tag active" onclick="selectDataSource('NOAA GOES-16')">NOAA GOES-16</div>
                                <div class="source-tag" onclick="selectDataSource('NASA OMNIWeb')">NASA OMNIWeb</div>
                                <div class="source-tag" onclick="selectDataSource('GFZ Potsdam')">GFZ Potsdam</div>
                                <div class="source-tag" onclick="selectDataSource('NASA CDDIS')">NASA CDDIS</div>
                                <div class="source-tag" onclick="selectDataSource('IRI-2020')">IRI-2020</div>
                                <div class="source-tag" onclick="selectDataSource('COSMIC-2')">COSMIC-2</div>
                            </div>
                            <!-- Small Live Data Source Detail Drawer -->
                            <div class="source-detail-drawer" id="source-detail-drawer">
                                <div style="font-weight:700; color:var(--accent-gold); font-size:0.72rem;" id="src-drawer-title">NOAA GOES-16 // NOAA SWPC</div>
                                <div style="font-size:0.68rem; opacity:0.85; margin-top:2px;" id="src-drawer-desc">Solar X-ray Flux (0.1-0.8 nm) &amp; Magnetometer · 1-minute real-time via HTTPS JSON API.</div>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>

        <!-- SLIDE 7: STATION MAP -->"""

content = re.sub(old_html_pattern, new_html, content, count=1, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Updated index.html: length is {len(content)} (delta: {len(content) - orig_len})")
