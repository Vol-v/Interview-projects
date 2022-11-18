import sys
import inspect

from typing import Optional
from fastapi import FastAPI, Request, Header, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import SessionLocal, engine
import models
from models import Product, ProductCategory, Category


#normally I would use migrations I think
models.Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


templates = Jinja2Templates(directory="templates")



@app.on_event("startup")
def startup_populate_db():
    db = SessionLocal()
    
    db.query(Product).delete()
    db.query(Category).delete()
    db.query(ProductCategory).delete()

    num_products = db.query(Product).count()
    num_categories = db.query(Category).count()
    num_link = db.query(ProductCategory).count()

    if not num_products:    
        product_dicts = [
            {'name':'Vodka'},
            {'name':'Beer'},
            {'name':'Beef'},
            {'name':'Sausages'},
            {'name':'Smoothie'},
            {'name':'Car'}
        ]

        products = []

        for p in product_dicts:
            products.append(Product(**p))

    if not num_categories:
        category_dicts = [
            {'name':'Food'},
            {'name':'Drinks'},
            {'name':'Books'},
        ]

        categories = []

        for c in category_dicts:
            categories.append(Category(**c))

    #hardcoding db relations
    products[0].categories.append(categories[1])
    products[1].categories.append(categories[1])
    products[2].categories.append(categories[0])
    products[3].categories.append(categories[0])
    products[4].categories.append(categories[0]) #smoothie has 2 categories
    products[4].categories.append(categories[1])

    #unnecessary
    # categories[0].products.append(products[2])
    # categories[0].products.append(products[3])
    # categories[0].products.append(products[4])
    # categories[1].products.append(products[0])
    # categories[1].products.append(products[1])
    # categories[1].products.append(products[4])

    for p in products:
        db.add(p)
    for c in categories:
        db.add(c)

    db.commit()

@app.get('/index/',response_class=HTMLResponse)
async def productlist(
    request:Request, 
    hx_request: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    ):

    products = db.query(Product).all()
    categories = db.query(Category).all()
    pairs = db.query(ProductCategory,Product,Category).filter(ProductCategory.category_id == Category.id, 
    ProductCategory.product_id == Product.id).with_entities(Product.name.label('product_label'),
    Category.name.label('category_label')).all()

    context = {'request':request,'products':products,'categories':categories,'pairs':pairs}
    if hx_request:
        return templates.TemplateResponse('table.html',context)
    return templates.TemplateResponse("index.html",context)