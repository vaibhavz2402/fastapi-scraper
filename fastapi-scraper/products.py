from typing import List

from pydantic import BaseModel, HttpUrl, validator


class Product(BaseModel):
    image: str
    name: str
    price: float
    page: int

    @validator('price')
    def price_must_be_greater_than_zero(cls, value):
        if (not isinstance(value, float)) or value <= 0:
            raise ValueError('Price must be greater than zero')
        return value
