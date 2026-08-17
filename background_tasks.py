import requests
import smtplib
import os
from email.message import EmailMessage
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor

executor = ProcessPoolExecutor(max_workers=2)

class BackgroundTaskQueue:
    def submit(self, task, *args, **kwargs):
        executor.submit(task, *args, **kwargs)

# Global instance
bg_queue = BackgroundTaskQueue()

# Actual blocking tasks
def _send_whatsapp_task(mobile, text, token, phone_id):
    try:
        url = f"http://10.255.255.1/timeout" # FAKE BLACKHOLE URL
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
        # Timeout ensures it doesn't hang forever
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        print(f"[WhatsApp Background] Sent to {mobile}, Status: {response.status_code}")
    except Exception as e:
        print(f"[WhatsApp Background] Error sending to {mobile}: {str(e)}")

def _send_email_task(smtp_server, smtp_port, smtp_username, smtp_password, to_email, subject, body, attachment_bytes, attachment_filename):
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = smtp_username
        msg['To'] = to_email
        msg.set_content(body)
        
        if attachment_bytes:
            msg.add_attachment(
                attachment_bytes,
                maintype='application',
                subtype='zip',
                filename=attachment_filename
            )
            
        if int(smtp_port) == 465:
            server = smtplib.SMTP_SSL(smtp_server, int(smtp_port), timeout=10)
        else:
            server = smtplib.SMTP(smtp_server, int(smtp_port), timeout=10)
            server.starttls()
            
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        print("[Email Background] Backup email sent successfully.")
    except Exception as e:
        print(f"[Email Background] Failed to send backup email: {e}")
