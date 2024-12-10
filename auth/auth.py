from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from jose import JWTError, jwt

load_dotenv()

SECRET_KEY = os.getenv('secret')
ALGORITHM = os.getenv('algorithm')
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(username: str, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = {"sub": username}
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Decode and verify the JWT token
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None