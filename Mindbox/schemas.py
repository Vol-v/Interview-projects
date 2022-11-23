from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str

class CategoryBase(BaseModel):
    name: str

class ProductCategoryBase(BaseModel):
    product_id: int
    category_id: int

    class Config:
        orm_mode = True

