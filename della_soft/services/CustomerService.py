from ..repositories.CustomerRepository import select_all


def select_all_customer_service():
    customers = select_all()
    print (customers)
    return customers