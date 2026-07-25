import subprocess
import time
import os
import signal

if __name__ == '__main__':
    print("Starting Flask server...")
    proc = subprocess.Popen(["python", "app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(3) # Wait for server to start
    
    print("Running socket tests...")
    test_proc = subprocess.Popen(["python", "test_sockets.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = test_proc.communicate()
    
    print(stdout.decode())
    if stderr:
        print("ERRORS:")
        print(stderr.decode())
        
    print("Killing server...")
    # Kill the process
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except:
        proc.kill()
