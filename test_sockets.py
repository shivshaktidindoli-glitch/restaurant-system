import socketio
import time
import requests
import threading
import sys

# Create a Socket.IO client for the Admin
admin_sio = socketio.Client()
server_url = "http://127.0.0.1:5000"
event_received = False

@admin_sio.event
def connect():
    print("[Admin] Connected to Socket.IO server!")

@admin_sio.event
def new_waiter_call(data):
    global event_received
    print(f"\n[Admin] SUCCESS! Received 'new_waiter_call' event: {data}")
    event_received = True

@admin_sio.event
def connect_error(data):
    print(f"[Admin] Connection failed: {data}")

def run_admin():
    try:
        admin_sio.connect(server_url)
        admin_sio.wait()
    except Exception as e:
        print(f"[Admin] Exception: {e}")

if __name__ == '__main__':
    print("Testing Waiter Calling Socket...")
    
    # Start admin socket in a background thread
    t = threading.Thread(target=run_admin)
    t.daemon = True
    t.start()
    
    # Wait for connection
    time.sleep(2)
    
    if not admin_sio.connected:
        print("Failed to connect admin socket.")
        sys.exit(1)
        
    print("\n[Customer] Sending REST POST to /api/call_waiter...")
    try:
        resp = requests.post(f"{server_url}/api/call_waiter", json={
            'table_name': 'T1',
            'order_id': 1
        }, timeout=5)
        print(f"[Customer] Response Code: {resp.status_code}")
    except Exception as e:
        print(f"[Customer] Request Failed: {e}")
        
    print("\nWaiting 5 seconds to see if admin receives the event...")
    for _ in range(5):
        if event_received:
            break
        time.sleep(1)
        
    if event_received:
        print("\nTEST PASSED: Socket event successfully transmitted.")
        sys.exit(0)
    else:
        print("\nTEST FAILED: Admin did not receive the 'new_waiter_call' socket event.")
        sys.exit(1)
