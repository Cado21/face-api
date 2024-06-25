from flask import Flask
from api import create_app
from firebase_setup import initialize_firebase
from flask_cors import CORS

initialize_firebase()

app = create_app()
CORS(app)

if __name__ == "__main__":
    app.run(debug=True)
