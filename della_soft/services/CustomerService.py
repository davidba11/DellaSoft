from ..repositories.CustomerRepository import select_all, select_by_name, select_by_parameter, create_customer, select_by_id, delete_customer, get_total_items, get_customer_section
from ..models.CustomerModel import Customer

async def select_all_customer_service():
    customers = select_all()
    #print (customers)
    return customers

async def select_by_parameter_service(value: str):
    if value.strip():  # Verifica que no esté vacío
        return select_by_parameter(value)  # Usa la nueva función que busca en nombre, apellido e ID
    return select_all()  # Si está vacío, devuelve todos los registros

def select_by_id_service(id: int):
    return select_by_id(id)

def select_by_name_service(name: str):
    return select_by_name(name)

def select_name_by_id(customer_id: int) -> str:
    """Obtiene el nombre del cliente a partir de su ID."""
    customer = select_by_id(customer_id)
    if customer:
        return f"{customer[0].first_name} {customer[0].last_name}"
    else:
        raise ValueError(f"No se encontró un cliente con ID {customer_id}")

def create_customer_service(id: int, first_name: str, last_name: str, contact: str, div: int):
    customer = select_by_id(id)
    if(len(customer) == 0):
        customer_save = Customer(id=id, first_name=first_name, last_name=last_name, contact=contact, div=div)
        return create_customer(customer_save)
    else:
        raise ValueError("Ya existe un cliente con ese ID.")
    
def delete_customer_service(id: int):
    return delete_customer(id)  

def get_total_items_service():
    return get_total_items()

def get_customer_section_service(offset: int, limit: int):
    return get_customer_section(offset, limit)

def get_customer_id_by_name_service(name: str) -> int:
    customer = select_by_name(name)  # Busca el cliente por nombre
    if customer:
        return customer.id  # Retorna el id del cliente encontrado
    else:
        raise ValueError(f"Cliente con nombre {name} no encontrado.")