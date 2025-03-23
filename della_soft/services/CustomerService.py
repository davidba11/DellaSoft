from ..repositories.CustomerRepository import select_all, select_by_name, create_customer, select_by_id
from ..models.CustomerModel import Customer

def select_all_customer_service():
    customers = select_all()
    print (customers)
    return customers

def select_by_name_service(name: str):
    if(len(name) != 0):
        return select_by_name(name)
    else:
        return select_all()
def create_customer_service(id: int, first_name: str, last_name: str, contact: str, div: int):
    customer = select_by_id(id)
    if(len(customer) == 0):
        customer_save = Customer(id=id, first_name=first_name, last_name=last_name, contact=contact, div=div)
        return create_customer(customer_save)
    else:
        print("El cliente ya existe")
        raise BaseException("El cliente ya existe")