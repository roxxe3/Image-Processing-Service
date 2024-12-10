from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import sessionmaker
from models.user import create_user, UserLogin
from auth.auth import create_access_token, decode_access_token
from auth.hash_pass import hash_password, verify_password
from database import engine, User

Session = sessionmaker(bind=engine)
session = Session()

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def add_user(username, password):
    new_user = User(username=username, password=hash_password(password))
    session.add(new_user)
    session.commit()
    return True

def check_user(form: UserLogin):
    user = session.query(User).filter(User.username == form.username).first()
    if user and verify_password(form.password, user.password):
        return True
    return False

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    user = session.query(User).filter(User.username == payload.get("sub")).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/signup")
async def signup(user: create_user):
    add_user(user.username, user.password)
    return create_access_token(user.username)

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = session.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/test", dependencies=[Depends(get_current_user)])
def hello():
    return "hello world"

# Example of a protected endpoint
@app.get("/user/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Example of another protected endpoint
@app.put("/user/me")
async def update_user_me(username: str, current_user: User = Depends(get_current_user)):
    current_user.username = username
    session.commit()
    return current_user