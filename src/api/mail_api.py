import requests
from ..config.constants import BASE_URL

class MailAPI:
    def __init__(self, token=None):
        self.token = token

    def _make_request(self, method, endpoint, data=None, auth=True):
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
        response = self._make_request('GET', '/domains', auth=False)
        return response.get('hydra:member', []) if response else []

    def create_account(self, email, password):
        """Create a new account"""
        data = {"address": email, "password": password}
        return self._make_request('POST', '/accounts', data=data, auth=False)

    def get_token(self, email, password):
        """Get authentication token"""
        data = {"address": email, "password": password}
        response = self._make_request('POST', '/token', data=data, auth=False)
        return response.get('token') if response else None

    def get_messages(self, page=1):
        """Retrieve messages with pagination"""
        response = self._make_request('GET', f'/messages?page={page}')
        return response.get('hydra:member', []) if response else []

    def get_message(self, message_id):
        """Get a specific message by ID"""
        return self._make_request('GET', f'/messages/{message_id}')

    def mark_as_read(self, message_id):
        """Mark message as read"""
        return self._make_request('PATCH', f'/messages/{message_id}', data={"seen": True})

    def delete_message(self, message_id):
        """Delete a message"""
        return self._make_request('DELETE', f'/messages/{message_id}') 