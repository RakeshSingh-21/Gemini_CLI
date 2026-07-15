from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class CategoryBase(BaseModel):
    name: str

class Category(CategoryBase):
    id: int

    class Config:
        orm_mode = True

class BrandBase(BaseModel):
    name: str

class Brand(BrandBase):
    id: int

    class Config:
        orm_mode = True

class ProductReviewBase(BaseModel):
    rating: int
    comment: str

class ProductReviewCreate(ProductReviewBase):
    pass

class ProductReview(ProductReviewBase):
    id: int
    user_id: int
    product_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    image_url: Optional[str] = None
    category_id: int
    brand_id: int

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    category: Category
    brand: Brand
    reviews: List[ProductReview] = []

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    role: str
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItem(CartItemBase):
    id: int
    product: Product
    class Config:
        orm_mode = True

class Cart(BaseModel):
    id: int
    items: List[CartItem]
    class Config:
        orm_mode = True

class OrderItem(BaseModel):
    product: Product
    quantity: int
    price: float
    class Config:
        orm_mode = True

class Order(BaseModel):
    id: int
    total_price: float
    status: str
    created_at: datetime
    items: List[OrderItem]
    class Config:
        orm_mode = True
