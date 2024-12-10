from passlib.context import CryptContext

# Create a password context to use bcrypt hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash the password
def hash_password(password: str):
    return pwd_context.hash(password)

# Verify the password matches the hashed password
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
