import sys
import inspect

from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from database import SessionLocal, engine
import models
from models import Product, ProductCategory, Category
from schemas import ProductBase, CategoryBase


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
# create container for our data - to be loaded at app startup.
data = []


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

@app.get('/products/',response_class=JSONResponse)
async def product_list(
    request:Request, 
    db: Session = Depends(get_db),
    ):

    products = db.query(Product).all()
    return JSONResponse(content=jsonable_encoder(products))


@app.get('/categories/',response_class=JSONResponse)
async def categories_list(
    request: Request,
    db: Session = Depends(get_db),
    ):
    categories = db.query(Category).all()
    context = {'request':request, 'categories':categories}
    return JSONResponse(content=jsonable_encoder(categories))



@app.get('/pairs/',response_class=JSONResponse)
async def pairs_list(
    request:Request,
    db: Session = Depends(get_db)
    ):
    prod_cat_table = db.query(ProductCategory).all()
    pairs = db.query(ProductCategory,Product,Category).filter(ProductCategory.category_id == Category.id, 
    ProductCategory.product_id == Product.id).with_entities(Product.name.label('product_label'),
    Category.name.label('category_label')).all()
    assert (len(pairs) == len(prod_cat_table))
    return JSONResponse(content=jsonable_encoder(pairs))


@app.post("/products/",response_model=ProductBase,status_code=200)
def post_product(product:ProductBase):
    #job_object = Job(**job.dict(), owner_id=owner_id)
    new_product = Product(name=product.name)
    db = get_db()
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@app.post("/categories/",response_model=CategoryBase,status_code=200)
def post_category(category: CategoryBase):
    #job_object = Job(**job.dict(), owner_id=owner_id)
    new_category = Category(name=category.name)
    db = get_db()
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category