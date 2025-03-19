from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import json
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.services.email_service import EmailService

app = Flask(__name__)
socketio = SocketIO(app)
email_service = EmailService()

def message_callback(data):
    """Handle new message notification via WebSocket"""
    socketio.emit('new_message', {'data': data})

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html', email=email_service.email)

@app.route('/messages')
def get_messages():
    """Get all messages"""
    messages = email_service.get_messages()
    return jsonify([msg.to_dict() for msg in messages])

@app.route('/message/<message_id>')
def get_message(message_id):
    """Get specific message"""
    message = email_service.get_message(message_id)
    if message:
        content = message.parse_content()
        return jsonify({
            **message.to_dict(),
            'otp': content['otp'],
            'url': content['url']
        })
    return jsonify({'error': 'Message not found'}), 404

def start_web():
    """Initialize and start the web application"""
    if not email_service.initialize():
        print("Failed to initialize email service")
        return False
    
    email_service.start_sse_listener(callback=message_callback)
    socketio.run(app, debug=True, port=5000)
    return True

if __name__ == '__main__':
    start_web() 