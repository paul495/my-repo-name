import requests
import json
import time
import sys

# Wait for server to start
time.sleep(3)

url = "http://127.0.0.1:5001/transcribe"
try:
    with open('sample.mp4', 'rb') as f:
        files = {'video': f}
        r = requests.post(url, files=files)
    
    print("Status Code:", r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)
except Exception as e:
    print("Test failed:", str(e))
    sys.exit(1)
