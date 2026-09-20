import subprocess, time, urllib.request, json, websocket, base64

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
proc = subprocess.Popen([
    edge_path,
    "--remote-debugging-port=9222",
    "--remote-allow-origins=*",
    "--headless=new",
    "--window-size=1600,900",
    "--user-data-dir=C:\\Users\\PARAM\\Desktop\\AEGIS\\scratch\\edge_prof",
    "http://127.0.0.1:8000/"
])
time.sleep(2.0)

try:
    res = urllib.request.urlopen("http://127.0.0.1:9222/json")
    tabs = json.loads(res.read().decode("utf-8"))
    ws_url = tabs[0]["webSocketDebuggerUrl"]
    ws = websocket.create_connection(ws_url, suppress_origin=True)
    
    # Let's inspect currentSlide and window state
    check_code = """
    (function() {
        return {
            currentSlide: typeof currentSlide !== 'undefined' ? currentSlide : null,
            totalSlides: typeof totalSlides !== 'undefined' ? totalSlides : null,
            isAnimating: typeof isAnimating !== 'undefined' ? isAnimating : null,
            slide5_display: document.getElementById('slide-5') ? window.getComputedStyle(document.getElementById('slide-5')).display : null,
            slide5_visibility: document.getElementById('slide-5') ? window.getComputedStyle(document.getElementById('slide-5')).visibility : null,
            slide5_opacity: document.getElementById('slide-5') ? window.getComputedStyle(document.getElementById('slide-5')).opacity : null,
            slide5_transform: document.getElementById('slide-5') ? window.getComputedStyle(document.getElementById('slide-5')).transform : null,
            container_transform: document.querySelector('.slides-container') ? window.getComputedStyle(document.querySelector('.slides-container')).transform : null
        };
    })();
    """
    ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": check_code, "returnByValue": True}}))
    resp = json.loads(ws.recv())
    print("Initial state:", resp.get("result", {}).get("value"))
    
    # Now jump to slide-5
    jump_code = """
    (function() {
        // remove preloader
        const p = document.querySelector('.preloader');
        if (p) p.remove();
        
        // Find slide-5 index
        const slides = Array.from(document.querySelectorAll('.slide'));
        const idx = slides.findIndex(s => s.id === 'slide-5');
        
        // Force jump without waiting for gsap
        slides.forEach(s => s.classList.remove('active'));
        slides[idx].classList.add('active');
        
        const container = document.querySelector('.slides-container');
        if (container) {
            container.style.transform = `translate3d(0, -${idx * (100 / slides.length)}%, 0)`;
        }
        
        // call fetchMethodology if needed
        if (typeof fetchMethodology === 'function') fetchMethodology();
        
        return { targetIdx: idx };
    })();
    """
    ws.send(json.dumps({"id": 2, "method": "Runtime.evaluate", "params": {"expression": jump_code, "returnByValue": True}}))
    resp = json.loads(ws.recv())
    print("Jump state:", resp.get("result", {}).get("value"))
    
    time.sleep(1.0)
    
    # Capture screenshot
    ws.send(json.dumps({"id": 3, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == 3:
            break
    img_data = base64.b64decode(r["result"]["data"])
    with open("scratch/slide_8_debug.png", "wb") as f:
        f.write(img_data)
    print("Saved scratch/slide_8_debug.png")
    ws.close()
except Exception as e:
    print("Error:", e)
finally:
    subprocess.run(["taskkill", "/F", "/IM", "msedge.exe"], capture_output=True)
