from pydantic import BaseModel
from typing import Optional, Tuple

class Resize(BaseModel):
    width: Optional[int]
    height: Optional[int]

class Crop(BaseModel):
    width: int
    height: int
    x: int
    y: int

class Filters(BaseModel):
    BLUR: Optional[bool] = False
    CONTOUR: Optional[bool] = False
    DETAIL: Optional[bool] = False
    EDGE_ENHANCE: Optional[bool] = False
    EDGE_ENHANCE_MORE: Optional[bool] = False
    FIND_EDGES: Optional[bool] = False
    SHARPEN: Optional[bool] = False
    SMOOTH: Optional[bool] = False
    SMOOTH_MORE: Optional[bool] = False

class Watermark(BaseModel):
    text: str
    position: Tuple[int, int] = (10, 10)

class Compress(BaseModel):
    quality: int = 85

class Transformations(BaseModel):
    resize: Optional[Resize]
    crop: Optional[Crop]
    rotate: Optional[int]
    flip: Optional[bool] = False
    mirror: Optional[bool] = False
    watermark: Optional[Watermark]
    compress: Optional[Compress]
    filters: Optional[Filters]
    # Remove the 'format' field
    # format: Optional[str] = None