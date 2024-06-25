import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials

def initialize_firebase():
    load_dotenv()
    cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    bucket_name = os.getenv('FIREBASE_STORAGE_BUCKET')

    if cred_path and bucket_name:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {'storageBucket': bucket_name})
    else:
        raise ValueError("The GOOGLE_APPLICATION_CREDENTIALS or FIREBASE_STORAGE_BUCKET environment variable is not set")
