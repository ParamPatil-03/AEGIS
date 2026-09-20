import subprocess, time, urllib.request, json, websocket, base64

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
proc = subprocess.Popen([
    edge_path,
    "--remote-debugging-port=9222",
    "--remote-allow-origins=*",
    "--headless=new",
    "--window-size=1600,900",
    "--user-data-dir=C:\\Users\\PARAM\\Desktop\\AEGIS\\scratch\\edge_prof",
    "http://127.0.0.1:8000/?slide=7"
])
time.sleep(3.0)

try:
    res = urllib.request.urlopen("http://127.0.0.1:9222/json")
    tabs = json.loads(res.read().decode("utf-8"))
    ws_url = tabs[0]["webSocketDebuggerUrl"]
    ws = websocket.create_connection(ws_url, suppress_origin=True)
    
    time.sleep(1.0)
    eval_code = """
    (function() {
        const p = document.querySelector('.preloader');
        if (p) p.style.display = 'none';
        isAnimating = false;
        goToSlide(7);
        if (typeof fetchMethodology === 'function') fetchMethodology();
    })();
    """
    ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": eval_code}}))
    time.sleep(2.0)
    
    ws.send(json.dumps({"id": 2, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == 2:
            break
    img_data = base64.b64decode(resp["result"]["data"])
    with open("scratch/slide_8.png", "wb") as f:
        f.write(img_data)
    print("SUCCESS: Screenshot saved to scratch/slide_8.png")
    ws.close()
except Exception as e:
    print("Error:", e)
finally:
    subprocess.run(["taskkill", "/F", "/IM", "msedge.exe"], capture_output=True)
