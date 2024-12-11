import boto3
from PIL import Image

s3 = boto3.resource('s3')
bucket_name='imagesbucketpillow'
region="eu-west-3"

def upload_image(path: str):
    im = Image.open(path)
    width, height = im.size
    with open(path, 'rb') as data:
        s3.Bucket(bucket_name).put_object(Key=path, Body=data)
    data = {
        "filename": path,
        "url": f"https://{bucket_name}.s3.{region}.amazonaws.com/{path}",
        "format": im.format,
        "width": width,
        "height": height
    }
    return data


print(upload_image("Hamza.png"))