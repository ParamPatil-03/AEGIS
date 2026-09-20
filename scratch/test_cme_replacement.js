const fs = require('fs');

const code = `
    let cmeRenderer, cmeScene, cmeCamera;
    let cmeAnimId = null;
    let cmeStartTime = 0;
    const cmeDuration = 12.0;
    let cmePhase = -1;
    let cmeHasPlayed = false;

    const CME_PHASES = [
      { name: 'SOLAR CORONA', start: 0, end: 0.167, label: 'CORONA' },
      { name: 'CME ERUPTION DETECTED', start: 0.167, end: 0.333, label: 'ERUPTION' },
      { name: 'INTERPLANETARY TRANSIT · ETA 18h', start: 0.333, end: 0.583, label: 'TRANSIT' },
      { name: 'MAGNETOSPHERE IMPACT · GEOMAGNETIC STORM', start: 0.583, end: 0.75, label: 'IMPACT' },
      { name: 'AEGIS SYSTEM ACTIVE · IONOSPHERIC MONITORING', start: 0.75, end: 1.0, label: 'AEGIS' }
    ];

    function replayCMESimulation() {
      cmeStartTime = performance.now() / 1000;
      cmePhase = -1;
      cmeHasPlayed = false;
      if (typeof AegisAudio !== 'undefined') AegisAudio.playBlip(1200, 0.04);
    }

    function jumpToCMEPhase(phaseIndex) {
      if (phaseIndex >= 0 && phaseIndex < CME_PHASES.length) {
        cmeStartTime = performance.now() / 1000 - CME_PHASES[phaseIndex].start * cmeDuration;
        cmePhase = -1;
        if (typeof AegisAudio !== 'undefined') AegisAudio.playBlip(1100, 0.03);
      }
    }

    function latLonToVector3(lat, lon, radius) {
      const phi = (90 - lat) * (Math.PI / 180);
      const theta = (lon + 180) * (Math.PI / 180);
      const x = -(radius * Math.sin(phi) * Math.cos(theta));
      const z = radius * Math.sin(phi) * Math.sin(theta);
      const y = radius * Math.cos(phi);
      return new THREE.Vector3(x, y, z);
    }

    // ──── Texture helpers (procedural, no external assets) ────

    function hexToRgbStr(hex) {
      const n = parseInt(hex.replace('#', ''), 16);
      return \`\${(n >> 16) & 255},\${(n >> 8) & 255},\${n & 255}\`;
    }

    function makeSoftDotTexture(hex = '#ffffff') {
      const rgb = hexToRgbStr(hex);
      const c = document.createElement('canvas');
      c.width = c.height = 128;
      const ctx = c.getContext('2d');
      const g = ctx.createRadialGradient(64, 64, 0, 64, 64, 64);
      g.addColorStop(0.0, \`rgba(\${rgb},1)\`);
      g.addColorStop(0.2, \`rgba(\${rgb},0.85)\`);
      g.addColorStop(0.4, \`rgba(\${rgb},0.5)\`);
      g.addColorStop(0.65, \`rgba(\${rgb},0.18)\`);
      g.addColorStop(1.0, \`rgba(\${rgb},0)\`);
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, 128, 128);
      const tex = new THREE.CanvasTexture(c);
      tex.needsUpdate = true;
      return tex;
    }

    function makeGlowSprite(hex, size, opacity) {
      const mat = new THREE.SpriteMaterial({
        map: makeSoftDotTexture(hex),
        color: 0xffffff,
        transparent: true,
        opacity,
        blending: THREE.AdditiveBlending,
        depthWrite: false
      });
      const spr = new THREE.Sprite(mat);
      spr.scale.set(size, size, 1);
      return spr;
    }

    function makeFresnelGlowMesh(radius, hex, { coefficient = 0.5, power = 2.2, opacity = 1, segments = 48 } = {}) {
      const material = new THREE.ShaderMaterial({
        uniforms: {
          glowColor: { value: new THREE.Color(hex) },
          coefficient: { value: coefficient },
          power: { value: power },
          opacity: { value: opacity }
        },
        vertexShader: \`
          varying vec3 vNormal;
          void main() {
            vNormal = normalize( normalMatrix * normal );
            gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
          }
        \`,
        fragmentShader: \`
          uniform vec3 glowColor;
          uniform float coefficient;
          uniform float power;
          uniform float opacity;
          varying vec3 vNormal;
          void main() {
            float intensity = pow( coefficient - dot( vNormal, vec3(0.0, 0.0, 1.0) ), power );
            gl_FragColor = vec4( glowColor, clamp(intensity, 0.0, 1.0) * opacity );
          }
        \`,
        side: THREE.BackSide,
        blending: THREE.AdditiveBlending,
        transparent: true,
        depthWrite: false
      });
      return new THREE.Mesh(new THREE.SphereGeometry(radius, segments, segments), material);
    }

    function makeSunTexture() {
      const c = document.createElement('canvas');
      c.width = 512; c.height = 256;
      const ctx = c.getContext('2d');
      ctx.fillStyle = '#FF8C00';
      ctx.fillRect(0, 0, 512, 256);
      const base = ctx.createLinearGradient(0, 0, 0, 256);
      base.addColorStop(0, '#FFD27A');
      base.addColorStop(0.5, '#FF9A2E');
      base.addColorStop(1, '#E5620A');
      ctx.fillStyle = base;
      ctx.fillRect(0, 0, 512, 256);
      for (let i = 0; i < 260; i++) {
        const x = Math.random() * 512;
        const y = Math.random() * 256;
        const r = 4 + Math.random() * 14;
        const g = ctx.createRadialGradient(x, y, 0, x, y, r);
        const bright = Math.random() > 0.5;
        g.addColorStop(0, bright ? 'rgba(255,235,180,0.45)' : 'rgba(150,40,0,0.35)');
        g.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.fill();
      }
      const tex = new THREE.CanvasTexture(c);
      tex.needsUpdate = true;
      return tex;
    }

    function makeEarthTexture() {
      const c = document.createElement('canvas');
      c.width = 512; c.height = 256;
      const ctx = c.getContext('2d');
      const ocean = ctx.createLinearGradient(0, 0, 0, 256);
      ocean.addColorStop(0, '#0d3a63');
      ocean.addColorStop(0.5, '#0a2d52');
      ocean.addColorStop(1, '#08213d');
      ctx.fillStyle = ocean;
      ctx.fillRect(0, 0, 512, 256);

      function blob(cx, cy, rx, ry, color) {
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.ellipse(cx, cy, rx, ry, Math.random() * Math.PI, 0, Math.PI * 2);
        ctx.fill();
      }
      const landSpots = [
        [90, 90, 55, 30], [150, 130, 40, 55], [250, 70, 70, 35],
        [300, 150, 50, 40], [400, 100, 60, 30], [430, 170, 35, 45],
        [60, 180, 30, 25], [200, 190, 45, 20]
      ];
      landSpots.forEach(([x, y, rx, ry]) => blob(x, y, rx, ry, 'rgba(45,90,55,0.85)'));
      landSpots.forEach(([x, y, rx, ry]) => blob(x + 6, y - 4, rx * 0.5, ry * 0.5, 'rgba(90,120,60,0.5)'));

      const capN = ctx.createLinearGradient(0, 0, 0, 40);
      capN.addColorStop(0, 'rgba(230,240,250,0.9)');
      capN.addColorStop(1, 'rgba(230,240,250,0)');
      ctx.fillStyle = capN;
      ctx.fillRect(0, 0, 512, 40);
      const capS = ctx.createLinearGradient(0, 216, 0, 256);
      capS.addColorStop(0, 'rgba(230,240,250,0)');
      capS.addColorStop(1, 'rgba(230,240,250,0.9)');
      ctx.fillStyle = capS;
      ctx.fillRect(0, 216, 512, 40);

      const tex = new THREE.CanvasTexture(c);
      tex.needsUpdate = true;
      return tex;
    }

    function makeAuroraRingTexture(rgbaHex) {
      const c = document.createElement('canvas');
      c.width = c.height = 256;
      const ctx = c.getContext('2d');
      const g = ctx.createRadialGradient(128, 128, 40, 128, 128, 128);
      g.addColorStop(0.0, 'rgba(0,0,0,0)');
      g.addColorStop(0.45, rgbaHex.replace(/[\\d.]+\\)$/, '0.15)'));
      g.addColorStop(0.62, rgbaHex);
      g.addColorStop(0.8, rgbaHex.replace(/[\\d.]+\\)$/, '0.2)'));
      g.addColorStop(1.0, 'rgba(0,0,0,0)');
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, 256, 256);
      const tex = new THREE.CanvasTexture(c);
      tex.needsUpdate = true;
      return tex;
    }

    function smoothstep(t) { return t * t * (3 - 2 * t); }

    function buildCameraPath(sunPos, earthPos) {
      return [
        { t: 0.00, pos: [0, 26, 300], look: [sunPos.x * 0.35, 4, 0] },
        { t: 0.167, pos: [-70, 14, 200], look: [sunPos.x + 20, 2, 0] },
        { t: 0.333, pos: [-30, 12, 190], look: [-10, 0, 0] },
        { t: 0.583, pos: [70, 8, 175], look: [earthPos.x - 25, 0, 0] },
        { t: 0.75, pos: [130, 10, 130], look: [earthPos.x, 0, 0] },
        { t: 1.00, pos: [158, 9, 55], look: [earthPos.x + 6, 2, 0] }
      ];
    }

    function sampleCameraPath(path, t) {
      t = Math.max(0, Math.min(1, t));
      let i = 0;
      while (i < path.length - 2 && t > path[i + 1].t) i++;
      const a = path[i], b = path[i + 1];
      const local = (t - a.t) / (b.t - a.t || 1);
      const e = smoothstep(Math.max(0, Math.min(1, local)));
      const pos = new THREE.Vector3().fromArray(a.pos).lerp(new THREE.Vector3().fromArray(b.pos), e);
      const look = new THREE.Vector3().fromArray(a.look).lerp(new THREE.Vector3().fromArray(b.look), e);
      return { pos, look };
    }

    function initCMESimulation() {
      if (typeof THREE === 'undefined') return;
      const container = document.getElementById('cme-sim-container');
      if (!container) return;

      const width = container.clientWidth || 800;
      const height = container.clientHeight || 480;

      cmeScene = new THREE.Scene();
      cmeCamera = new THREE.PerspectiveCamera(50, width / height, 0.1, 2000);
      cmeCamera.position.set(0, 26, 300);

      cmeRenderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      cmeRenderer.setSize(width, height);
      cmeRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      cmeRenderer.toneMapping = THREE.ACESFilmicToneMapping;
      cmeRenderer.toneMappingExposure = 1.15;
      if ('outputColorSpace' in cmeRenderer) cmeRenderer.outputColorSpace = THREE.SRGBColorSpace;
      container.insertBefore(cmeRenderer.domElement, container.firstChild);

      // ──── STARFIELD ────
      const starCount = 1400;
      const starPositions = new Float32Array(starCount * 3);
      const starSizes = new Float32Array(starCount);
      for (let i = 0; i < starCount; i++) {
        starPositions[i * 3] = (Math.random() - 0.5) * 1600;
        starPositions[i * 3 + 1] = (Math.random() - 0.5) * 1200;
        starPositions[i * 3 + 2] = (Math.random() - 0.5) * 800 - 200;
        starSizes[i] = 0.6 + Math.random() * 1.6;
      }
      const starColors = new Float32Array(starCount * 3);
      const starPalette = ['#FFFFFF', '#CFE3FF', '#FFF3D6'];
      for (let i = 0; i < starCount; i++) {
        const col = new THREE.Color(starPalette[Math.floor(Math.random() * starPalette.length)]);
        starColors[i * 3] = col.r; starColors[i * 3 + 1] = col.g; starColors[i * 3 + 2] = col.b;
      }
      const starGeo = new THREE.BufferGeometry();
      starGeo.setAttribute('position', new THREE.Float32BufferAttribute(starPositions, 3));
      starGeo.setAttribute('color', new THREE.Float32BufferAttribute(starColors, 3));
      const starMat = new THREE.PointsMaterial({
        color: 0xffffff, size: 1.1, transparent: true, opacity: 0.7, vertexColors: true,
        map: makeSoftDotTexture('#ffffff'), depthWrite: false, sizeAttenuation: true
      });
      const starField = new THREE.Points(starGeo, starMat);
      cmeScene.add(starField);

      // ──── SUN ────
      const sunGroup = new THREE.Group();
      sunGroup.position.set(-160, 0, 0);
      cmeScene.add(sunGroup);

      const sunTexture = makeSunTexture();
      const sunMesh = new THREE.Mesh(
        new THREE.SphereGeometry(32, 48, 32),
        new THREE.MeshBasicMaterial({ map: sunTexture })
      );
      sunGroup.add(sunMesh);

      sunGroup.add(makeFresnelGlowMesh(34, '#FFCC66', { coefficient: 0.45, power: 2.4, opacity: 1.4 }));
      sunGroup.add(makeFresnelGlowMesh(40, '#FF8C33', { coefficient: 0.3, power: 3.2, opacity: 0.9 }));
      sunGroup.add(makeGlowSprite('#FF7A22', 240, 0.14));

      // ──── EARTH ────
      const earthGroup = new THREE.Group();
      earthGroup.position.set(140, 0, 0);
      cmeScene.add(earthGroup);

      const R = 18;
      const earthTexture = makeEarthTexture();
      const earthMesh = new THREE.Mesh(
        new THREE.SphereGeometry(R, 48, 32),
        new THREE.MeshBasicMaterial({ map: earthTexture })
      );
      earthGroup.add(earthMesh);

      const earthWireGeo = new THREE.SphereGeometry(R + 0.15, 28, 14);
      const earthWireMat = new THREE.MeshBasicMaterial({
        color: 0x00E5FF, wireframe: true, transparent: true, opacity: 0.08
      });
      earthGroup.add(new THREE.Mesh(earthWireGeo, earthWireMat));

      earthGroup.add(makeFresnelGlowMesh(R * 1.06, '#5FB8FF', { coefficient: 0.55, power: 3.5, opacity: 1.2 }));
      earthGroup.add(makeFresnelGlowMesh(R * 1.16, '#3B82F6', { coefficient: 0.3, power: 4.0, opacity: 0.7 }));

      // ──── MAGNETOSPHERE (Bow Shock) ────
      const magnetoGroup = new THREE.Group();
      magnetoGroup.visible = false;
      earthGroup.add(magnetoGroup);

      const bowShockMat = new THREE.MeshBasicMaterial({
        color: 0x8B5CF6, transparent: true, opacity: 0.0,
        side: THREE.DoubleSide, blending: THREE.AdditiveBlending, wireframe: true
      });
      const bowShock = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 24), bowShockMat);
      bowShock.scale.set(38, 28, 28);
      bowShock.position.set(-8, 0, 0);
      magnetoGroup.add(bowShock);

      const mpMat = new THREE.MeshBasicMaterial({
        color: 0x00E5FF, transparent: true, opacity: 0.0,
        side: THREE.DoubleSide, blending: THREE.AdditiveBlending, wireframe: true
      });
      const magnetopause = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 18), mpMat);
      magnetopause.scale.set(30, 22, 22);
      magnetopause.position.set(-5, 0, 0);
      magnetoGroup.add(magnetopause);

      const fieldLineGroup = new THREE.Group();
      magnetoGroup.add(fieldLineGroup);
      for (let k = 0; k < 4; k++) {
        const curve = new THREE.CatmullRomCurve3([
          new THREE.Vector3(0, R + 2, 0),
          new THREE.Vector3(-12 - k * 4, R + 8 + k * 3, 0),
          new THREE.Vector3(-20 - k * 6, 0, 0),
          new THREE.Vector3(-12 - k * 4, -(R + 8 + k * 3), 0),
          new THREE.Vector3(0, -(R + 2), 0)
        ]);
        const flGeo = new THREE.BufferGeometry().setFromPoints(curve.getPoints(30));
        const fl = new THREE.Line(flGeo, new THREE.LineBasicMaterial({
          color: 0x8B5CF6, transparent: true, opacity: 0.4
        }));
        fl.rotation.z = k * (Math.PI / 5) - Math.PI / 10;
        fieldLineGroup.add(fl);
      }

      const impactFlash = makeGlowSprite('#BFEFFF', 4, 0);
      earthGroup.add(impactFlash);

      // ──── POLAR AURORA ────
      const auroraGroup = new THREE.Group();
      auroraGroup.visible = false;
      earthGroup.add(auroraGroup);

      function makeAuroraRing(hex, y, sign) {
        const geo = new THREE.RingGeometry(R * 0.22, R * 0.55, 48);
        const mat = new THREE.MeshBasicMaterial({
          map: makeAuroraRingTexture(hex), transparent: true, opacity: 0,
          side: THREE.DoubleSide, blending: THREE.AdditiveBlending, depthWrite: false
        });
        const ring = new THREE.Mesh(geo, mat);
        ring.rotation.x = Math.PI / 2;
        ring.position.y = y;
        return ring;
      }
      const auroraN = makeAuroraRing('rgba(60,220,120,0.9)', R * 0.9, 1);
      const auroraS = makeAuroraRing('rgba(150,90,220,0.85)', -R * 0.9, -1);
      auroraGroup.add(auroraN, auroraS);

      // ──── CME PARTICLE CLOUD ────
      const cmeParticleCount = 2500;
      const cmePositions = new Float32Array(cmeParticleCount * 3);
      const cmeVelocities = [];
      for (let i = 0; i < cmeParticleCount; i++) {
        cmePositions[i * 3] = 0; cmePositions[i * 3 + 1] = 0; cmePositions[i * 3 + 2] = 0;
        const speed = 0.8 + Math.random() * 1.2;
        cmeVelocities.push(new THREE.Vector3(speed, (Math.random() - 0.5) * 0.4, (Math.random() - 0.5) * 0.4));
      }
      const cmeColors = new Float32Array(cmeParticleCount * 3);
      const hotColor = new THREE.Color('#FFF4D6');
      const coolColor = new THREE.Color('#FF4419');
      for (let i = 0; i < cmeParticleCount; i++) {
        const col = hotColor.clone().lerp(coolColor, Math.pow(Math.random(), 1.6));
        cmeColors[i * 3] = col.r; cmeColors[i * 3 + 1] = col.g; cmeColors[i * 3 + 2] = col.b;
      }
      const cmeParticleGeo = new THREE.BufferGeometry();
      cmeParticleGeo.setAttribute('position', new THREE.Float32BufferAttribute(cmePositions, 3));
      cmeParticleGeo.setAttribute('color', new THREE.Float32BufferAttribute(cmeColors, 3));
      const cmeParticleMat = new THREE.PointsMaterial({
        color: 0xffffff, size: 3.0, map: makeSoftDotTexture('#ffffff'), vertexColors: true,
        transparent: true, opacity: 0.0, blending: THREE.AdditiveBlending,
        sizeAttenuation: true, depthWrite: false
      });
      const cmeParticles = new THREE.Points(cmeParticleGeo, cmeParticleMat);
      cmeParticles.position.copy(sunGroup.position);
      cmeScene.add(cmeParticles);

      const flashMat = new THREE.SpriteMaterial({
        map: makeSoftDotTexture('#ffffff'), transparent: true, opacity: 0.0,
        blending: THREE.AdditiveBlending, depthWrite: false
      });
      const flashMesh = new THREE.Sprite(flashMat);
      flashMesh.scale.set(16, 16, 1);
      flashMesh.position.set(30, 4, 0);
      sunGroup.add(flashMesh);

      // ──── DEFLECTED IMPACT PARTICLES ────
      const splashCount = 600;
      const splashPositions = new Float32Array(splashCount * 3);
      const splashVelocities = [];
      for (let i = 0; i < splashCount; i++) {
        splashPositions[i * 3] = 0; splashPositions[i * 3 + 1] = 0; splashPositions[i * 3 + 2] = 0;
        const angle = Math.random() * Math.PI * 2;
        const speed = 0.3 + Math.random() * 0.5;
        splashVelocities.push(new THREE.Vector3(-0.1 + Math.random() * 0.3, Math.sin(angle) * speed, Math.cos(angle) * speed));
      }
      const splashColors = new Float32Array(splashCount * 3);
      const splashHot = new THREE.Color('#EAFBFF');
      const splashCool = new THREE.Color('#3FB6E8');
      for (let i = 0; i < splashCount; i++) {
        const col = splashHot.clone().lerp(splashCool, Math.random());
        splashColors[i * 3] = col.r; splashColors[i * 3 + 1] = col.g; splashColors[i * 3 + 2] = col.b;
      }
      const splashGeo = new THREE.BufferGeometry();
      splashGeo.setAttribute('position', new THREE.Float32BufferAttribute(splashPositions, 3));
      splashGeo.setAttribute('color', new THREE.Float32BufferAttribute(splashColors, 3));
      const splashMat = new THREE.PointsMaterial({
        color: 0xffffff, size: 2.0, map: makeSoftDotTexture('#ffffff'), vertexColors: true,
        transparent: true, opacity: 0.0, blending: THREE.AdditiveBlending,
        sizeAttenuation: true, depthWrite: false
      });
      const splashParticles = new THREE.Points(splashGeo, splashMat);
      splashParticles.position.copy(earthGroup.position);
      splashParticles.position.x -= 30;
      cmeScene.add(splashParticles);

      // ──── AEGIS REGIONAL MONITORING STATIONS ────
      const aegisStationsGroup = new THREE.Group();
      aegisStationsGroup.visible = false;
      earthGroup.add(aegisStationsGroup);

      const stationsData = [
        { code: 'LCK', lat: 26.85, lon: 80.9, color: 0x22C55E },
        { code: 'HYD', lat: 17.40, lon: 78.5, color: 0xEAB308 },
        { code: 'BLR', lat: 12.90, lon: 77.6, color: 0xEAB308 },
        { code: 'CMB', lat: 6.90, lon: 79.9, color: 0x22C55E }
      ];
      const stationBeams = [];
      stationsData.forEach(st => {
        const pos = latLonToVector3(st.lat, st.lon, R + 0.5);
        const pin = new THREE.Mesh(new THREE.SphereGeometry(0.8, 12, 12), new THREE.MeshBasicMaterial({ color: st.color }));
        pin.position.copy(pos);
        aegisStationsGroup.add(pin);

        const beamTop = pos.clone().normalize().multiplyScalar(R + 8);
        const beamGeo = new THREE.BufferGeometry().setFromPoints([pos, beamTop]);
        const beam = new THREE.Line(beamGeo, new THREE.LineBasicMaterial({ color: st.color, transparent: true, opacity: 0.85 }));
        aegisStationsGroup.add(beam);
        stationBeams.push({ beam });
      });

      const ionoRippleMat = new THREE.MeshBasicMaterial({
        color: 0xFF6633, transparent: true, opacity: 0.0, wireframe: true, blending: THREE.AdditiveBlending
      });
      const ionoRipple = new THREE.Mesh(new THREE.SphereGeometry(R + 5, 32, 24), ionoRippleMat);
      earthGroup.add(ionoRipple);

      const connMat = new THREE.LineDashedMaterial({ color: 0xFFAA33, dashSize: 4, gapSize: 3, transparent: true, opacity: 0.0 });
      const connLine = new THREE.Line(new THREE.BufferGeometry().setFromPoints([sunGroup.position.clone(), earthGroup.position.clone()]), connMat);
      connLine.computeLineDistances();
      cmeScene.add(connLine);

      cmeScene.add(new THREE.AmbientLight(0x333344, 0.5));

      const cameraPath = buildCameraPath(sunGroup.position, earthGroup.position);

      // ──── TIMELINE INTERACTION ────
      const timelineEl = document.getElementById('cme-timeline');
      if (timelineEl) {
        timelineEl.addEventListener('click', (e) => {
          const rect = timelineEl.getBoundingClientRect();
          const frac = (e.clientX - rect.left) / rect.width;
          cmeStartTime = performance.now() / 1000 - frac * cmeDuration;
          cmePhase = -1;
          if (typeof AegisAudio !== 'undefined') AegisAudio.playBlip(1100, 0.03);
        });
      }

      // ──── DRAG TO ROTATE EARTH ────
      let isDragging = false;
      let prevMX = 0, prevMY = 0;
      let holdRotVelX = 0, holdRotVelY = 0;

      container.addEventListener('mousedown', (e) => { isDragging = true; prevMX = e.clientX; prevMY = e.clientY; holdRotVelX = 0; holdRotVelY = 0; });
      window.addEventListener('mouseup', () => { isDragging = false; });
      container.addEventListener('mousemove', (e) => {
        if (!isDragging || !cmeHasPlayed) return;
        const dx = e.clientX - prevMX, dy = e.clientY - prevMY;
        prevMX = e.clientX; prevMY = e.clientY;
        holdRotVelX = dx * 0.003; holdRotVelY = dy * 0.002;
        earthGroup.rotation.y += holdRotVelX;
        earthGroup.rotation.x += holdRotVelY;
      });

      const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      cmeStartTime = performance.now() / 1000;
      let impactFlashPeak = 0;

      function animate() {
        cmeAnimId = requestAnimationFrame(animate);
        const now = performance.now() / 1000;
        const elapsed = now - cmeStartTime;
        const t = Math.min(elapsed / cmeDuration, 1.0);

        const fillEl = document.getElementById('cme-timeline-fill');
        if (fillEl) fillEl.style.width = (t * 100) + '%';

        let newPhase = -1;
        for (let i = 0; i < CME_PHASES.length; i++) {
          if (t >= CME_PHASES[i].start && t < CME_PHASES[i].end) { newPhase = i; break; }
        }
        if (t >= 1.0) newPhase = 4;

        if (newPhase !== cmePhase) {
          cmePhase = newPhase;
          const labelEl = document.getElementById('cme-phase-label');
          if (labelEl && cmePhase >= 0) labelEl.textContent = CME_PHASES[cmePhase].name;
          document.querySelectorAll('.cme-tl-phase').forEach(el => {
            el.classList.toggle('active', parseInt(el.dataset.phase) === cmePhase);
          });
          if (cmePhase === 3) impactFlashPeak = now;
          if (typeof AegisAudio !== 'undefined' && cmePhase >= 0) {
            AegisAudio.playBlip(900 + cmePhase * 120, 0.035);
          }
        }

        let pLocal = 0;
        if (cmePhase >= 0 && cmePhase < CME_PHASES.length) {
          const ph = CME_PHASES[cmePhase];
          pLocal = Math.max(0, Math.min(1, (t - ph.start) / (ph.end - ph.start)));
        }

        const cam = sampleCameraPath(cameraPath, t);
        cmeCamera.position.copy(cam.pos);
        cmeCamera.lookAt(cam.look);

        starMat.opacity = 0.65 + 0.08 * Math.sin(now * 1.3);
        sunMesh.rotation.y += prefersReduced ? 0 : 0.0015;

        if (cmePhase >= 1) {
          if (cmePhase === 1) {
            const flashIntensity = pLocal < 0.3 ? pLocal / 0.3 : Math.max(0, 1 - (pLocal - 0.3) / 0.7);
            flashMat.opacity = flashIntensity * 0.9;
            flashMesh.scale.set(16 * (1 + flashIntensity * 2), 16 * (1 + flashIntensity * 2), 1);
          } else {
            flashMat.opacity = 0;
          }
          if (cmePhase === 1 && pLocal < 0.1) {
            const positions = cmeParticleGeo.attributes.position.array;
            for (let i = 0; i < cmeParticleCount; i++) {
              positions[i * 3] = 28 + Math.random() * 6;
              positions[i * 3 + 1] = (Math.random() - 0.5) * 12;
              positions[i * 3 + 2] = (Math.random() - 0.5) * 12;
            }
            cmeParticleGeo.attributes.position.needsUpdate = true;
          }
          cmeParticleMat.opacity = Math.min(0.85, cmeParticleMat.opacity + 0.02);
        }

        if (cmePhase >= 1 && cmePhase <= 2 && !prefersReduced) {
          const positions = cmeParticleGeo.attributes.position.array;
          for (let i = 0; i < cmeParticleCount; i++) {
            positions[i * 3] += cmeVelocities[i].x * 1.2;
            positions[i * 3 + 1] += cmeVelocities[i].y * 0.3;
            positions[i * 3 + 2] += cmeVelocities[i].z * 0.3;
          }
          cmeParticleGeo.attributes.position.needsUpdate = true;
          connMat.opacity = Math.min(0.25, connMat.opacity + 0.005);
        }

        if (cmePhase >= 3) {
          magnetoGroup.visible = true;
          const magFade = cmePhase === 3 ? Math.min(1, pLocal * 3) : 1;
          bowShockMat.opacity = 0.18 * magFade;
          mpMat.opacity = 0.14 * magFade;

          const boom = Math.max(0, 1 - (now - impactFlashPeak) / 0.6);
          impactFlash.material.opacity = boom * 0.8;
          impactFlash.scale.setScalar(R * 2 + boom * R * 3);

          if (cmePhase === 3) {
            const compress = 1 - pLocal * 0.15;
            bowShock.scale.x = 38 * compress;
            magnetopause.scale.x = 30 * compress;
            cmeParticleMat.opacity = Math.max(0, 0.85 - pLocal * 0.9);
          }

          if (cmePhase === 3) {
            splashMat.opacity = Math.min(0.7, pLocal * 1.5);
            if (!prefersReduced) {
              const sPositions = splashGeo.attributes.position.array;
              for (let i = 0; i < splashCount; i++) {
                sPositions[i * 3] += splashVelocities[i].x * 0.5;
                sPositions[i * 3 + 1] += splashVelocities[i].y * 0.5;
                sPositions[i * 3 + 2] += splashVelocities[i].z * 0.5;
              }
              splashGeo.attributes.position.needsUpdate = true;
            }
          } else if (cmePhase > 3) {
            splashMat.opacity = Math.max(0, splashMat.opacity - 0.01);
          }

          auroraGroup.visible = true;
          const auroraIntensity = cmePhase === 3 ? pLocal : 1;
          auroraN.material.opacity = 0.85 * auroraIntensity;
          auroraS.material.opacity = 0.8 * auroraIntensity;
          if (!prefersReduced) { auroraN.rotation.z += 0.01; auroraS.rotation.z -= 0.008; }
        }

        if (cmePhase >= 4) {
          aegisStationsGroup.visible = true;
          const rippleT = cmePhase === 4 ? pLocal : 1;
          ionoRippleMat.opacity = 0.12 * (1 - rippleT * 0.5);
          ionoRipple.scale.setScalar(1 + rippleT * 0.15);
          if (!prefersReduced) {
            stationBeams.forEach((sb, idx) => { sb.beam.material.opacity = 0.5 + 0.4 * Math.sin(now * 4 + idx); });
          }
          earthGroup.rotation.y = THREE.MathUtils.lerp(earthGroup.rotation.y, -(78 * Math.PI / 180), 0.04);
          earthGroup.rotation.x = THREE.MathUtils.lerp(earthGroup.rotation.x, 0.28, 0.04);

          if (t >= 1.0) {
            cmeHasPlayed = true;
            const labelEl = document.getElementById('cme-phase-label');
            if (labelEl) labelEl.textContent = 'SIMULATION COMPLETE · DRAG TO EXPLORE';
          }
        }

        if (cmeHasPlayed && !isDragging && !prefersReduced) {
          holdRotVelX *= 0.95; holdRotVelY *= 0.95;
          earthGroup.rotation.y += holdRotVelX;
          earthGroup.rotation.x += holdRotVelY;
          if (Math.abs(holdRotVelX) < 0.0001) earthGroup.rotation.y += 0.001;
        }

        cmeRenderer.render(cmeScene, cmeCamera);
      }

      animate();

      window.addEventListener('resize', () => {
        if (!container || !cmeRenderer || !cmeCamera) return;
        const w = container.clientWidth, h = container.clientHeight;
        if (w > 0 && h > 0) {
          cmeCamera.aspect = w / h;
          cmeCamera.updateProjectionMatrix();
          cmeRenderer.setSize(w, h);
        }
      });
    }
`;

try {
  new Function(code);
  console.log("CME Replacement Code: Valid JavaScript syntax!");
} catch (e) {
  console.error("Syntax Error:", e);
}
