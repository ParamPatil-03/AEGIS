import subprocess, time, urllib.request, json, websocket, base64

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
proc = subprocess.Popen([
    edge_path,
    "--remote-debugging-port=9222",
    "--remote-allow-origins=*",
    "--headless=new",
    "--window-size=1600,900",
    "--user-data-dir=C:\\Users\\PARAM\\Desktop\\AEGIS\\scratch\\edge_prof",
    "http://127.0.0.1:8000/?slide=6"
])
time.sleep(2.5)

try:
    res = urllib.request.urlopen("http://127.0.0.1:9222/json")
    tabs = json.loads(res.read().decode("utf-8"))
    ws_url = tabs[0]["webSocketDebuggerUrl"]
    ws = websocket.create_connection(ws_url, suppress_origin=True)
    
    time.sleep(1.0)
    ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": "goToSlide(6);"}}))
    time.sleep(1.5)
    
    ws.send(json.dumps({"id": 2, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == 2:
            break
    img_data = base64.b64decode(resp["result"]["data"])
    with open("scratch/slide_7.png", "wb") as f:
        f.write(img_data)
    print("SUCCESS: Screenshot saved to scratch/slide_7.png")
    ws.close()
except Exception as e:
    print("Error:", e)
finally:
    subprocess.run(["taskkill", "/F", "/IM", "msedge.exe"], capture_output=True)
