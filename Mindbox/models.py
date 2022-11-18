import sys

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    categories = relationship("Category", secondary="product_category")


class ProductCategory(Base):
    __tablename__ = "product_category"

    product_id = Column(Integer,ForeignKey('product.id'),primary_key=True)
    category_id = Column(Integer,ForeignKey('category.id'),primary_key=True)

class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    products = relationship("Product", secondary="product_category")