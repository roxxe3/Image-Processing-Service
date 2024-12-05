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


@app.get("/")
def hello():
    return "hello world"


@app.post("/signup")
async def signup(user: create_user):
    add_user(user.username, user.password)
    return encode_jwt(user.username, user.password)

if __name__ == "__main__":
    app.run()