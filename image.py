import boto3
from PIL import Image
from fastapi import UploadFile, HTTPException
from io import BytesIO
from botocore.exceptions import ClientError
from models.image import Transformations
import requests
import hashlib
import aioredis
import json


def generate_cache_key(url: str, transformation: Transformations) -> str:
    # Generate a unique cache key based on the image URL and transformation parameters
    key = f"{url}-{transformation.json()}"
    return hashlib.md5(key.encode()).hexdigest()

redis = aioredis.from_url("redis://localhost")

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
    """
    Fetches an image from a given URL, applies specified transformations, and uploads the transformed image to an S3 bucket.
    Args:
        url (str): The URL of the image to be fetched.
        transformation (Transformations): An object containing the transformations to be applied to the image.
    Returns:
        dict: A dictionary containing the URL of the uploaded transformed image.
    Raises:
        HTTPException: If there is an error fetching the image or processing the image.
    """
    cache_key = generate_cache_key(url, transformation)
    
    # Check if the transformed image is already in the cache
    cached_result = await redis.get(cache_key)
    if cached_result:
        return json.loads(cached_result)

    try:
        response = requests.get(url)
        filename = url.split('/')[-1]
        extension = filename.split('.')[-1] if '.' in filename else None
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        
        # Resize image
        if transformation.resize and transformation.resize.width > 0 and transformation.resize.height > 0:
            img = img.resize((transformation.resize.width, transformation.resize.height))

        # Crop image
        if transformation.crop and transformation.crop.width > 0 and transformation.crop.height > 0:
            left = transformation.crop.x
            upper = transformation.crop.y
            right = left + transformation.crop.width
            lower = upper + transformation.crop.height

            # Ensure crop dimensions are within image bounds
            left = max(0, left)
            upper = max(0, upper)
            right = min(img.width, right)
            lower = min(img.height, lower)

            if right > left and lower > upper:  # Valid crop area
                img = img.crop((left, upper, right, lower))
            else:
                print("Skipping crop: Invalid crop dimensions")

        image_format = transformation.format.lower() if transformation.format.lower() in ["jpeg", "png", "bmp", "gif"] else img.format.lower()

        # Rotate image
        if transformation.rotate:
            img = img.rotate(transformation.rotate)

        # Convert to JPEG-compatible mode if needed
        if transformation.format.upper() == "JPEG" and img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        # Save the image with the desired format to a byte array
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format=image_format.upper())
        img_byte_arr.seek(0)

        # Upload the image to S3
        s3.Bucket(bucket_name).put_object(
            Key=f"transformed/{filename.split('.')[0]}.{image_format}",
            Body=img_byte_arr,
            ContentType=f"image/{image_format}"
        )
        result = {"url": f"https://{bucket_name}.s3.{region}.amazonaws.com/transformed/{filename.split('.')[0]}.{image_format}"}
        
        # Store the transformed image in the cache
        await redis.set(cache_key, json.dumps(result))
        return result
    
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