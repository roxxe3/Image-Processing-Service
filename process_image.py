from PIL import Image
import requests
from io import BytesIO
from image import upload_transformed_image

async def process_image_from_url(url, width, height):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img_resized = img.resize((width, height))
    img_resized.show()
    








    

