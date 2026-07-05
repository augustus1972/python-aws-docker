from flask import Flask
import socket
import platform

app = Flask(__name__)

@app.route('/')
def home():
    hostname = socket.gethostname()
    python_version = platform.python_version()
    return f"witaj w mojej aplikacji python (Python {python_version}) tj. Artura Kotarskiego zawieszonej w chmurze AWS, Serwer produkcyjny: {hostname}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
