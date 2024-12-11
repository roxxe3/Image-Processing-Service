from PIL import Image
import requests
from io import BytesIO
from image import upload_transformed_image

async def process_image_from_url(url, transformation):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    if transformation.resize:
        img_resized = img.resize((transformation.resize.width, transformation.resize.height))
        img_resized.show()
        await upload_transformed_image(url, transformation)

