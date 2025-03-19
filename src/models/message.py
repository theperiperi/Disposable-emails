import re
from html import unescape
from ..config.constants import REGEX

class Message:
    def __init__(self, message_data):
        self.id = message_data.get('id')
        self.subject = message_data.get('subject')
        self.text = message_data.get('text', '')
        self.html = message_data.get('html', [])
        self.seen = message_data.get('seen', False)

    def parse_content(self):
        """Parse email content for OTPs and URLs"""
        html_content = ' '.join(self.html)
        
        if html_content:
            html_content = re.sub(r'<[^>]+>', ' ', html_content)
            html_content = unescape(html_content)
        
        body = self.text + ' ' + html_content
        
        otp = re.search(REGEX['otp'], body)
        url = re.search(REGEX['url'], body)

        return {
            'otp': otp.group(1) if otp else None,
            'url': url.group(1) if url else None
        }

    def to_dict(self):
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'subject': self.subject,
            'text': self.text,
            'seen': self.seen
        } 