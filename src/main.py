import time
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.services.email_service import EmailService

def print_messages(messages):
    """Print messages in a formatted way"""
    if messages:
        for msg in messages:
            print(f"[{msg.id}] {msg.subject}")
    else:
        print("No messages found.")

def handle_new_message(data):
    """Handle new message notification"""
    print("\nNew message received!")

def main():
    """Main application entry point"""
    service = EmailService()

    if not service.initialize():
        print("Failed to initialize email service.")
        return

    print(f"Logged in as: {service.email}")
    
    # Start SSE listener
    if not service.start_sse_listener(callback=handle_new_message):
        print("SSE failed, using polling...")

    try:
        while True:
            print("\nOptions: [M] Messages | [Q] Quit | [OTP <id>] Get OTP | [O <id>] Open Email")
            choice = input("> ").strip().upper()

            if choice == "Q":
                break

            elif choice == "M":
                messages = service.get_messages()
                print_messages(messages)

            elif choice.startswith("OTP"):
                try:
                    _, msg_id = choice.split()
                    message = service.get_message(msg_id)
                    if message:
                        content = message.parse_content()
                        print(f"OTP: {content['otp']}")
                    else:
                        print("Message not found.")
                except ValueError:
                    print("Invalid command format. Use: OTP <message_id>")

            elif choice.startswith("O"):
                try:
                    _, msg_id = choice.split()
                    message = service.get_message(msg_id)
                    if message:
                        print(f"Subject: {message.subject}")
                        print(f"Content: {message.text}")
                    else:
                        print("Message not found.")
                except ValueError:
                    print("Invalid command format. Use: O <message_id>")
            
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main() 