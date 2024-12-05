from fastapi import FastAPI
from models.user import create_user, UserLogin
from auth.auth import encode_jwt, decode_jwt
import pymongo


myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["mydatabase"]
users_list= mydb["users"]


app=FastAPI()




@app.post("/signup")
async def signup(user: create_user):
    return encode_jwt(user.username, user.password)

if __name__ == "__main__":
    app.run()