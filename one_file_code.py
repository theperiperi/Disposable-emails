import os
import json
import requests
import threading
import time
import webbrowser
import re
from html import unescape
import sseclient

# Configuration
CONFIG_FILE = os.path.expanduser('~/.ote')
BASE_URL = "https://api.mail.tm"
MERCURE_URL = "https://mercure.mail.tm/.well-known/mercure"
REGEX = {
    'otp': r'(\d{4,8})',
    'url': r'(https?://[^\s<>"]+|www\.[^\s<>"]+)'
}

class OTE:
    def __init__(self):
        self.token = None
        self.account_id = None
        self.email = None
        self.password = None
        self.sse_thread = None
        self.load_config()
        
    def load_config(self):
        """Load config if available"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.email = config.get('email')
                self.password = config.get('password')
                self.token = config.get('token')
                self.account_id = config.get('account_id')

    def save_config(self):
        """Save configuration to file"""
        config = {
            'email': self.email,
            'password': self.password,
            'token': self.token,
            'account_id': self.account_id
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)

    def api_request(self, method, endpoint, data=None, auth=True):
        """Make API request to mail.tm"""
        url = f"{BASE_URL}{endpoint}"
        headers = {}
        
        if auth and self.token:
            headers['Authorization'] = f"Bearer {self.token}"
        
        if data:
            headers['Content-Type'] = 'application/json'
        
        try:
            response = requests.request(method, url, headers=headers, json=data)
            
            if response.status_code >= 200 and response.status_code < 300:
                if response.text:
                    return response.json()
                return True
            print(f"Error: {response.status_code} - {response.text}")
            return None
        except Exception as e:
            print(f"Request Error: {str(e)}")
            return None

    def get_domains(self):
        """Fetch available domains"""
        response = self.api_request('GET', '/domains', auth=False)
        return response.get('hydra:member', []) if response else []

    def create_account(self, email, password):
        """Create account and get token"""
        data = {"address": email, "password": password}
        response = self.api_request('POST', '/accounts', data=data, auth=False)

        if response:
            self.email = email
            self.password = password
            self.account_id = response['id']

            if self.get_token():  # Ensure token is fetched
                self.save_config()
                print(f"Account created: {self.email}")
                return True
        
        print("Failed to create account.")
        return False

    def get_token(self):
        """Get token after creating an account"""
        data = {"address": self.email, "password": self.password}
        response = self.api_request('POST', '/token', data=data, auth=False)

        if response and 'token' in response:
            self.token = response['token']
            return True

        print("Failed to get token.")
        return False

    def get_messages(self, page=1):
        """Retrieve messages with pagination"""
        response = self.api_request('GET', f'/messages?page={page}')
        return response.get('hydra:member', []) if response else []

    def get_message(self, message_id):
        """Get a specific message by ID"""
        return self.api_request('GET', f'/messages/{message_id}')

    def mark_as_read(self, message_id):
        """Mark message as read"""
        return self.api_request('PATCH', f'/messages/{message_id}', data={"seen": True})

    def delete_message(self, message_id):
        """Delete a message"""
        return self.api_request('DELETE', f'/messages/{message_id}')

    def parse_email_content(self, message):
        """Parse email for OTPs and URLs"""
        text_content = message.get('text', '')
        html_content = ' '.join(message.get('html', []))
        
        if html_content:
            html_content = re.sub(r'<[^>]+>', ' ', html_content)
            html_content = unescape(html_content)
        
        body = text_content + ' ' + html_content
        
        otp = re.search(REGEX['otp'], body)
        url = re.search(REGEX['url'], body)

        otp_value = otp.group(1) if otp else None
        url_value = url.group(1) if url else None
        
        return otp_value, url_value

    def start_sse_listener(self):
        """Real-time email listener"""
        if not self.token or not self.account_id:
            return False

        def listen():
            headers = {'Authorization': f'Bearer {self.token}'}
            url = f"{MERCURE_URL}?topic=/accounts/{self.account_id}"

            try:
                response = requests.get(url, headers=headers, stream=True)
                client = sseclient.SSEClient(response)

                for event in client.events():
                    if event.data:
                        print("\nNew message received!")
            except Exception as e:
                print(f"SSE Error: {str(e)}")

        self.sse_thread = threading.Thread(target=listen)
        self.sse_thread.daemon = True
        self.sse_thread.start()
        return True

def main():
    """Main function"""
    ote = OTE()

    # If no account exists, create one
    if not ote.email or not ote.password or not ote.token:
        domains = ote.get_domains()
        if not domains:
            print("Failed to fetch domains.")
            return

        # Use random domain and username
        domain = domains[0]['domain']
        username = f"user{int(time.time())}"
        email = f"{username}@{domain}"
        password = "TempPass123!"

        if not ote.create_account(email, password):
            print("Failed to create account.")
            return

    print(f"Logged in as: {ote.email}")
    
    # Start SSE listener
    if not ote.start_sse_listener():
        print("SSE failed, using polling...")

    try:
        while True:
            print("\nOptions: [M] Messages | [Q] Quit | [OTP <id>] Get OTP | [O <id>] Open Email")
            choice = input("> ").strip().upper()

            if choice == "Q":
                break

            elif choice == "M":
                messages = ote.get_messages()
                if messages:
                    for msg in messages:
                        print(f"[{msg['id']}] {msg['subject']}")
                else:
                    print("No messages found.")

            elif choice.startswith("OTP"):
                _, msg_id = choice.split()
                message = ote.get_message(msg_id)
                otp, _ = ote.parse_email_content(message)
                print(f"OTP: {otp}")

            elif choice.startswith("O"):
                _, msg_id = choice.split()
                message = ote.get_message(msg_id)
                print(f"Subject: {message['subject']}")
                print(f"Content: {message.get('text', '')}")
            
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()