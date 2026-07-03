# server/app.py
from flask import Flask
from server.routes import initialize_routes

app = Flask(__name__)
app.json.compact = False  # Keep json responses readable

# Connect endpoints
initialize_routes(app)

if __name__ == '__main__':
    app.run(port=5555, debug=True)