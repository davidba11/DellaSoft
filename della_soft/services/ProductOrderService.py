from ..repositories.ProductOrderRespository import select_all


def select_all_product_order_service():
    products_order = select_all()
    print (products_order)
    return products_order