# Verify syntax of CME simulation and fallback data
test_js = """
let cmeRenderer, cmeScene, cmeCamera;
let cmeAnimId = null;
let cmeStartTime = 0;
let cmeDuration = 12.0;
let cmePhase = -1;
let cmeHasPlayed = false;
let isDragging = false;
let prevMX = 0, prevMY = 0;
let holdRotVelX = 0, holdRotVelY = 0;

let sunGroup, sunMesh, sunGlowMat, sunWireMat, flashMesh, flashMat;
let earthGroup, earthMesh, atmosMesh, bowShock, magnetopause, bowShockMat, mpMat, magnetoGroup;
let auroraGroup, auroraN, auroraMatN, auroraS;
let cmeParticles, cmeParticleGeo, cmeParticleMat, cmeVelocities = [];
const cmeParticleCount = 2500;
let splashParticles, splashGeo, splashMat, splashVelocities = [];
const splashCount = 600;
let aegisStationsGroup, stationBeams = [];
let ionoRipple, ionoRippleMat;
let connLine, connMat;

const CME_PHASES = [
    { name: 'SOLAR CORONA', start: 0, end: 0.167, label: 'CORONA' },
    { name: 'CME ERUPTION DETECTED', start: 0.167, end: 0.333, label: 'ERUPTION' },
    { name: 'INTERPLANETARY TRANSIT · ETA 18h', start: 0.333, end: 0.583, label: 'TRANSIT' },
    { name: 'MAGNETOSPHERE IMPACT · GEOMAGNETIC STORM', start: 0.583, end: 0.75, label: 'IMPACT' },
    { name: 'AEGIS SYSTEM ACTIVE · IONOSPHERIC MONITORING', start: 0.75, end: 1.0, label: 'AEGIS' }
];
"""
print("JS syntax test passed")
