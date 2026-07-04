from flask import Flask
import socket

app = Flask(__name__)

@app.route('/')
def home():
    hostname = socket.gethostname()
    return f"Witaj w mojej aplikacji Python! Serwer produkcyjny: {hostname}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
