import boto3
from PIL import Image
from fastapi import UploadFile, HTTPException
from io import BytesIO
from botocore.exceptions import ClientError
from models.image import Transformations
import requests

s3 = boto3.resource('s3')
bucket_name = 'imagesbucketpillow'
region = "eu-west-3"

# Allowed file types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

async def upload_image(file: UploadFile) -> dict:
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"File type not allowed. Allowed types: {ALLOWED_EXTENSIONS}"
        )

    try:
        contents = await file.read()
        
        image = Image.open(BytesIO(contents))
        width, height = image.size
        file_size = len(contents) / 1024
        

        s3.Bucket(bucket_name).put_object(
            Key=file.filename,
            Body=contents,
            ContentType=f'image/{file_ext}'
        )
        
        return {
            "filename": file.filename,
            "url": f"https://{bucket_name}.s3.{region}.amazonaws.com/{file.filename}",
            "format": image.format,
            "file_size": file_size,
            "width": width,
            "height": height
        }
    
    except ClientError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload to S3: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )
    finally:
        await file.close()

async def upload_transformed_image(url: str, transformation: Transformations):
    try:
        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))

        if transformation.resize:
            img = img.resize((transformation.resize.width, transformation.resize.height))
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format=transformation.format or img.format)
        img.show()
        img_byte_arr.seek(0)

        s3.put_object(
            Bucket=bucket_name,
            Key=f"transformed/{url.split('/')[-1]}",
            Body=img_byte_arr,
            ContentType=f"image/{transformation.format or img.format.lower()}"
        )
        return {"url": f"https://{bucket_name}.s3.{region}.amazonaws.com/transformed/{url.split('/')[-1]}"}
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching image: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )