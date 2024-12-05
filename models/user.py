from pydantic import BaseModel

class create_user(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str