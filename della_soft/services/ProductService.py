import asyncio
from ..repositories.ProductRepository import select_all, delete_product, get_product, insert_product
from ..models.ProductModel import Product

async def select_all_product_service():
    products = select_all()
    return products

def select_product(value: str):
    if(len(value) != 0):
        return get_product(value)
    else:
        return select_all()

def create_product(id: int, name: str, description: str, product_type: str):

    product_save = Product(id=id, name=name, description=description, product_type=product_type)
    return insert_product(product_save)

def delete_product_service(id: int):
    return delete_product(id)  