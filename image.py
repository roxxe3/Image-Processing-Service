import boto3
import os
from PIL import Image, ImageDraw, ImageFont
from fastapi import UploadFile, HTTPException
from PIL import ImageFilter
from io import BytesIO
from botocore.exceptions import ClientError
from models.image import Transformations
import requests

s3 = boto3.resource('s3')
bucket_name = os.getenv('BUCKET_NAME', 'default_bucket_name')
region = os.getenv('REGION', 'default_region')

# Allowed file types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def compress_image(image, quality=85):
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format=image.format, quality=quality)
    img_byte_arr.seek(0)
    return img_byte_arr
def flip_image(image):
    return image.transpose(Image.FLIP_TOP_BOTTOM)

def mirror_image(image):
    return image.transpose(Image.FLIP_LEFT_RIGHT)

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
    try:
        response = requests.get(url)
        filename = url.split('/')[-1]
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        
        # Use the original image format
        image_format = img.format.lower() if img.format else 'jpeg'  # Default to 'jpeg' if format is None

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

        # Rotate image
        if transformation.rotate:
            img = img.rotate(transformation.rotate)

        # Flip image
        if transformation.flip:
            img = flip_image(img)

        # Mirror image
        if transformation.mirror:
            img = mirror_image(img)

        # Add watermark
        if transformation.watermark and transformation.watermark.text:
            draw = ImageDraw.Draw(img)
            font = ImageFont.load_default()
            position = tuple(transformation.watermark.position) if transformation.watermark.position else (10, 10)
            draw.text(position, transformation.watermark.text, (255, 255, 255), font=font)


        # Apply filters
        if isinstance(transformation.filters, dict):
            if transformation.filters.get("BLUR"):
                img = img.filter(ImageFilter.BLUR)
            if transformation.filters.get("CONTOUR"):
                img = img.filter(ImageFilter.CONTOUR)
            if transformation.filters.get("DETAIL"):
                img = img.filter(ImageFilter.DETAIL)
            if transformation.filters.get("EDGE_ENHANCE"):
                img = img.filter(ImageFilter.EDGE_ENHANCE)
            if transformation.filters.get("EDGE_ENHANCE_MORE"):
                img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
            if transformation.filters.get("FIND_EDGES"):
                img = img.filter(ImageFilter.FIND_EDGES)
            if transformation.filters.get("SHARPEN"):
                img = img.filter(ImageFilter.SHARPEN)
            if transformation.filters.get("SMOOTH"):
                img = img.filter(ImageFilter.SMOOTH)
            if transformation.filters.get("SMOOTH_MORE"):
                img = img.filter(ImageFilter.SMOOTH_MORE)

        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format=image_format.upper())
        img_byte_arr.seek(0)
        s3.Bucket(bucket_name).put_object(
            Key=f"transformed/{filename.split('.')[0]}.{image_format}",
            Body=img_byte_arr,
            ContentType=f"image/{image_format}"
        )
        return {"url": f"https://{bucket_name}.s3.{region}.amazonaws.com/transformed/{filename.split('.')[0]}.{image_format}"}
    
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
