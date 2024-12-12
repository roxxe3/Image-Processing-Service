from PIL import Image
import requests
from io import BytesIO
from image import upload_transformed_image

async def process_image_from_url(url, width, height):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img_resized = img.resize((width, height))
    img_resized.show()
    






process_image_from_url("https://imagesbucketpillow.s3.eu-west-3.amazonaws.com/1712076948499.jpeg", 100, 200)


    

