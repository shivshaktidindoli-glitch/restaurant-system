import time
import requests
import os
import subprocess
import json
import threading

def run_server():
    print("[Test] Starting local eventlet server...")
    # Run the server directly using eventlet for accurate testing
    return subprocess.Popen(['python', 'app.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

def verify():
    # 1. Modify background_tasks.py to force a 5-second timeout delay by hitting a blackhole IP
    print("[Test] Modifying background_tasks.py to simulate 5s timeout...")
    with open('background_tasks.py', 'r') as f:
        original_tasks = f.read()
        
    with open('background_tasks.py', 'w') as f:
        f.write(original_tasks.replace('url = f"https://graph.facebook.com', 'url = f"http://10.255.255.1/timeout'))
        
    # 2. Modify .env to use a fake token
    print("[Test] Modifying .env with fake token...")
    with open('.env', 'r') as f:
        original_env = f.read()
        
    with open('.env', 'w') as f:
        new_env = original_env.replace('WHATSAPP_TOKEN=', 'WHATSAPP_TOKEN_BAK=').replace('WHATSAPP_PHONE_ID=', 'WHATSAPP_PHONE_ID_BAK=')
        f.write(new_env + '\nWHATSAPP_TOKEN=FAKE_TOKEN_123\nWHATSAPP_PHONE_ID=FAKE_ID_123')
        
    server_process = None
    try:
        server_process = run_server()
        time.sleep(3) # Wait for server to boot
        
        # Prepare Order Payload
        order_payload = {
            "table_name": "T-1",
            "customer_name": "Test User",
            "customer_mobile": "9999999999",
            "items": [{"id": 1, "name": "Test Item", "price": 100, "quantity": 1}],
            "order_type": "dine-in"
        }
        
        print("\n[Test] Testing /api/place_order...")
        start_time = time.time()
        res = requests.post('http://127.0.0.1:5000/api/place_order', json=order_payload)
        order_time = time.time() - start_time
        
        print(f"Order Placement Time: {order_time:.4f} seconds")
        print(f"Response: {res.status_code}")
        
        if res.status_code == 200:
            order_id = res.json().get('order_id')
            print(f"\n[Test] Testing /api/update_order_status for Order #{order_id}...")
            start_time = time.time()
            res2 = requests.post('http://127.0.0.1:5000/api/update_order_status', json={"order_id": order_id, "status": "preparing"})
            update_time = time.time() - start_time
            print(f"Status Update Time: {update_time:.4f} seconds")
        else:
            print("Failed to place order.")
            
        print("\n[Test] Waiting 6 seconds to observe background task timeout crash resilience...")
        time.sleep(6)
        
        # Check if server is still alive
        try:
            ping = requests.get('http://127.0.0.1:5000/ping')
            if ping.status_code == 200:
                print("[Test] SUCCESS: Server is STILL ALIVE and did not crash after background thread exception/timeout.")
        except Exception as e:
            print("[Test] FAILED: Server crashed!")
            
    finally:
        print("\n[Test] Cleaning up and restoring original files...")
        if server_process:
            server_process.terminate()
            
        with open('background_tasks.py', 'w') as f:
            f.write(original_tasks)
            
        with open('.env', 'w') as f:
            f.write(original_env)
            
if __name__ == '__main__':
    verify()
