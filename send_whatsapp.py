import sys
import requests

def main():
    if len(sys.argv) < 5:
        print("Usage: python send_whatsapp.py <mobile> <text> <token> <phone_id>")
        sys.exit(1)
        
    mobile = sys.argv[1]
    text = sys.argv[2]
    token = sys.argv[3]
    phone_id = sys.argv[4]
    
    # FAKE URL FOR TIMEOUT TESTING
    # url = f"http://10.255.255.1/timeout" 
    url = f"https://graph.facebook.com/v17.0/{phone_id}/messages"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": mobile,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": text
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        print(f"[WhatsApp] Sent to {mobile}, Status: {response.status_code}")
    except Exception as e:
        print(f"[WhatsApp] Error: {str(e)}")

if __name__ == '__main__':
    main()
