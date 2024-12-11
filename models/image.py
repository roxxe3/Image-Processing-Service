from pydantic import BaseModel
from typing import Optional

class Resize(BaseModel):
    width: Optional[int]
    height: Optional[int]

class Crop(BaseModel):
    width: int
    height: int
    x: int
    y: int

class Filters(BaseModel):
    grayscale: Optional[bool] = False
    sepia: Optional[bool] = False

class Transformations(BaseModel):
    resize: Optional[Resize]
    crop: Optional[Crop]
    rotate: Optional[int]
    format: Optional[str]
    filters: Optional[Filters]

