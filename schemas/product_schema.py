from pydantic import BaseModel, Field, PositiveFloat
from typing import List, Optional


class Product(BaseModel):
    id: int
    title: str
    description: str
    price: float
    rating: Optional[float] = None
    brand: Optional[str] = None
    category: Optional[str] = None

    model_config = {"populate_by_name": True}


class ProductListResponse(BaseModel):
    products: List[Product]
    total: int
    skip: int
    limit: int


class ProductCreateRequest(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    price: PositiveFloat


class ProductUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    price: Optional[PositiveFloat] = None
