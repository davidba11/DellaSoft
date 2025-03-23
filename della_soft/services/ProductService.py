from ..repositories.ProductRepository import select_all

def select_all_product_service():
    products = select_all()
    print (products)
    return products