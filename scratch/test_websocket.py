import asyncio
import json
import websockets

async def test_ws():
    uri = "ws://127.0.0.1:8000/ws/telemetry"
    print(f"Connecting to {uri}...")
    async with websockets.connect(uri) as ws:
        # 1. First message should be immediate telemetry push
        msg1_raw = await asyncio.wait_for(ws.recv(), timeout=5.0)
        msg1 = json.loads(msg1_raw)
        print("Received Handshake Telemetry Packet:")
        print(f"  - type: {msg1.get('type')}")
        print(f"  - alert_level: {msg1.get('alert_level')}")
        print(f"  - data_source: {msg1.get('data_source')}")
        print(f"  - space_weather: Kp={msg1.get('space_weather', {}).get('kp_index')}, Bz={msg1.get('space_weather', {}).get('imf_bz')} nT")
        print(f"  - stations_summary: {list(msg1.get('stations_summary', {}).keys())}")
        
        assert msg1.get('type') == 'telemetry_push', f"Expected telemetry_push, got {msg1.get('type')}"
        assert 'stations_summary' in msg1, "stations_summary missing from payload"
        assert len(msg1['stations_summary']) == 4, f"Expected 4 stations in summary, got {len(msg1['stations_summary'])}"

        # 2. Test ping-pong
        print("\nSending 'ping'...")
        await ws.send("ping")
        pong_raw = await asyncio.wait_for(ws.recv(), timeout=3.0)
        pong = json.loads(pong_raw)
        print("Received response:", pong)
        assert pong.get('type') == 'pong', f"Expected pong, got {pong.get('type')}"

        # 3. Test receiving next periodic push
        print("\nWaiting for next periodic push...")
        msg2_raw = await asyncio.wait_for(ws.recv(), timeout=6.0)
        msg2 = json.loads(msg2_raw)
        print("Received Periodic Push:")
        print(f"  - type: {msg2.get('type')}, alert_level: {msg2.get('alert_level')}")
        assert msg2.get('type') == 'telemetry_push'

    print("\n>>> ALL WEBSOCKET TESTS PASSED! <<<")

if __name__ == '__main__':
    asyncio.run(test_ws())
