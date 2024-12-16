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
    BLUR: Optional[bool] = False
    CONTOUR: Optional[bool] = False
    DETAIL: Optional[bool] = False
    EDGE_ENHANCE: Optional[bool] = False
    EDGE_ENHANCE_MORE: Optional[bool] = False
    EMBOSS: Optional[bool] = False
    FIND_EDGES: Optional[bool] = False
    SHARPEN: Optional[bool] = False
    SMOOTH: Optional[bool] = False
    SMOOTH_MORE: Optional[bool] = False

class Transformations(BaseModel):
    resize: Optional[Resize]
    crop: Optional[Crop]
    rotate: Optional[int]
    format: Optional[str]
    filters: Optional[Filters]

