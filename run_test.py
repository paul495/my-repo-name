import subprocess
import time
import requests
import socket
import sys

print("Starting Flask server...")
server = subprocess.Popen(["python", "app.py"])

print("Waiting for server to initialize and load the Whisper model...")
port_open = False
for _ in range(60):
    try:
        with socket.create_connection(("127.0.0.1", 5001), timeout=1):
            port_open = True
            break
    except OSError:
        time.sleep(1)

if not port_open:
    print("Server failed to start in time.")
    server.terminate()
    sys.exit(1)

print("Server is up! Sending the sample video for transcription...")
try:
    with open("sample.mp4", "rb") as f:
        r = requests.post("http://127.0.0.1:5001/transcribe", files={"video": f})
    
    print("Status Code:", r.status_code)
    try:
        import json
        print("Response JSON:")
        print(json.dumps(r.json(), indent=2)[:500] + "...\n[TRUNCATED FOR BREVITY]")
    except Exception:
        print("Response Text:", r.text)
        
    if r.status_code == 200:
        print("TEST PASSED!")
    else:
        print("TEST FAILED.")
        sys.exit(1)
finally:
    print("Terminating server...")
    server.terminate()
