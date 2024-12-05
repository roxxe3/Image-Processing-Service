from fastapi import FastAPI
from models.user import create_user, UserLogin
from auth.auth import encode_jwt, decode_jwt
import pymongo
from sqlalchemy.orm import sessionmaker
from database import engine, User

Session = sessionmaker(bind=engine)
session = Session()


app=FastAPI()


def add_user(username, password):
    new_user = User(username=username, password=password)
    session.add(new_user)
    session.commit()
    return True

def check_user(form: UserLogin):
    users = session.query(User).all()
    for user in users:
        if user.username == form.username and user.password == form.password:
            return True
    return False


@app.get("/")
def hello():
    return "hello world"


@app.post("/signup")
async def signup(user: create_user):
    add_user(user.username, user.password)
    return encode_jwt(user.username, user.password)

@app.post("/login")
async def user_login(form: UserLogin):
    if check_user(form):
        return encode_jwt(form.username, form.password)
    else:
        return {"message": "invalide login"}

if __name__ == "__main__":
    app.run()
