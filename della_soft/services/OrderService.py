from ..repositories.OrderRepository import select_all


def select_all_order_service():
    orders = select_all()
    print (orders)
    return orders