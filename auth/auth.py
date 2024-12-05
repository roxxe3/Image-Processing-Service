import jwt
import time
from dotenv import load_dotenv
import os



load_dotenv()

JWT_SECRET = os.getenv('secret')
JWT_ALGORITHM = os.getenv('algorithm')

def encode_jwt(username: str, password: str):
    payload = {
        "username": username,
        "password": password,
        "expiry": time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decode_jwt(token: str):
    try:
        decode_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return decode_token if decode_token["expires"] >= time.time() else None
    except:
        return {}