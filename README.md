# Disposable Email Client

A modular Python implementation of a disposable email client using mail.tm service. This client allows you to create temporary email addresses and receive emails, including OTP codes and verification links.

## Features

- Create temporary email addresses
- Receive emails in real-time using SSE
- Extract OTP codes and URLs from emails
- Simple command-line interface
- Modern web interface
- Persistent configuration

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd disposable-email
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

You can run the client using the `run.py` script:

### Command Line Interface

```bash
./run.py
```
or
```bash
python run.py
```

### Web Interface

```bash
./run.py --web
```
or
```bash
python run.py --web
```

Optional: Specify a custom port (default is 5000):
```bash
./run.py --web --port 8080
```

Then open your browser and navigate to `http://localhost:5000` (or your custom port).

### CLI Commands

- `M` - List all messages
- `O <id>` - Open and read a specific message
- `OTP <id>` - Extract OTP from a specific message
- `Q` - Quit the application

## Project Structure

```
src/
├── api/
│   └── mail_api.py         # API client implementation
├── config/
│   └── constants.py        # Configuration and constants
├── models/
│   └── message.py          # Message model
├── services/
│   └── email_service.py    # Main email service
├── web/
│   ├── templates/          # HTML templates
│   ├── static/             # Static files (CSS, JS)
│   └── app.py             # Web application
├── main.py                 # CLI entry point
└── launcher.py            # Application launcher
run.py                     # Main entry point script
```

## Configuration

The client stores configuration in `~/.ote` file, including:
- Email address
- Password
- Authentication token
- Account ID

## License

MIT License 