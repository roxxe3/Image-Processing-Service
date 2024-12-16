from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import sessionmaker
from models.user import create_user, UserLogin
from auth.auth import create_access_token, decode_access_token
from auth.hash_pass import hash_password, verify_password
from database import engine, User, Image
from image import upload_image, upload_transformed_image
from fastapi import File, UploadFile
from models.image import Transformations

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


async def image_meta_data(file: UploadFile, user_id: int):
    try:
        image_data = await upload_image(file)
        image = Image(
            user_id=user_id,
            filename=image_data["filename"],
            url=image_data["url"],
            width=image_data["width"],
            height=image_data["height"],
            file_size=image_data["file_size"],
            mime_type=image_data["format"]
        )
        session.add(image)
        session.commit()
        session.refresh(image)
        return image
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")















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

@app.get("/user/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.put("/user/me")
async def update_user_me(username: str, current_user: User = Depends(get_current_user)):
    current_user.username = username
    session.commit()
    return current_user

@app.post("/images")
async def post_image(
    file: UploadFile = File(..., description="The image file to upload"), 
    current_user: User = Depends(get_current_user)
):
    image = await image_meta_data(file, current_user.id)
    return {"message": "success", "image": image}

@app.get("/images/{id}")
async def get_image(id):
    image = session.query(Image).filter(Image.id == id).first()
    return image

@app.get("/images")
async def list_images(page: int = 1, limit: int = 10, current_user: User = Depends(get_current_user)):
    offset = (page - 1) * limit
    images = session.query(Image).filter(Image.user_id == current_user.id).offset(offset).limit(limit).all()
    return images

@app.put("/images/{id}/transform")
async def transform_image(
    id: str,
    transformation: Transformations, 
    current_user: User = Depends(get_current_user)
):
    image = session.query(Image).filter(
        Image.id == id,
        Image.user_id == current_user.id
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=404, 
            detail="Image not found or you don't have permission"
        )
    
    try:
        result = await upload_transformed_image(image.url, transformation)
        import json
        
        if image.transformations:
            current_transforms = json.loads(image.transformations)
            current_transforms.append(transformation.dict())
            image.transformations = json.dumps(current_transforms)
        else:
            image.transformations = json.dumps([transformation.dict()])
        
        session.commit()
        return {"message": "Image transformed successfully", "result": result}
        
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to transform image: {str(e)}"
        )