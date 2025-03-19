import json
import time
import threading
import sseclient
import requests
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.config.constants import CONFIG_FILE, MERCURE_URL, DEFAULT_PASSWORD
from src.api.mail_api import MailAPI
from src.models.message import Message

class EmailService:
    def __init__(self):
        self.api = MailAPI()
        self.email = None
        self.password = None
        self.account_id = None
        self.sse_thread = None
        self.load_config()

    def load_config(self):
        """Load configuration from file"""
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.email = config.get('email')
                self.password = config.get('password')
                self.account_id = config.get('account_id')
                self.api.token = config.get('token')
        except FileNotFoundError:
            pass

    def save_config(self):
        """Save configuration to file"""
        config = {
            'email': self.email,
            'password': self.password,
            'token': self.api.token,
            'account_id': self.account_id
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)

    def create_account(self, domain):
        """Create a new email account"""
        username = f"user{int(time.time())}"
        email = f"{username}@{domain}"
        
        response = self.api.create_account(email, DEFAULT_PASSWORD)
        if not response:
            return False

        self.email = email
        self.password = DEFAULT_PASSWORD
        self.account_id = response['id']
        
        token = self.api.get_token(email, DEFAULT_PASSWORD)
        if not token:
            return False

        self.api.token = token
        self.save_config()
        return True

    def get_messages(self, page=1):
        """Get messages and convert to Message objects"""
        messages_data = self.api.get_messages(page)
        return [Message(msg) for msg in messages_data]

    def get_message(self, message_id):
        """Get specific message"""
        message_data = self.api.get_message(message_id)
        return Message(message_data) if message_data else None

    def start_sse_listener(self, callback=None):
        """Start SSE listener for real-time updates"""
        if not self.api.token or not self.account_id:
            return False

        def listen():
            headers = {'Authorization': f'Bearer {self.api.token}'}
            url = f"{MERCURE_URL}?topic=/accounts/{self.account_id}"

            try:
                response = requests.get(url, headers=headers, stream=True)
                client = sseclient.SSEClient(response)

                for event in client.events():
                    if event.data and callback:
                        callback(event.data)
            except Exception as e:
                print(f"SSE Error: {str(e)}")

        self.sse_thread = threading.Thread(target=listen)
        self.sse_thread.daemon = True
        self.sse_thread.start()
        return True

    def initialize(self):
        """Initialize the service"""
        if not self.email or not self.password or not self.api.token:
            domains = self.api.get_domains()
            if not domains:
                return False
            return self.create_account(domains[0]['domain'])
        return True 