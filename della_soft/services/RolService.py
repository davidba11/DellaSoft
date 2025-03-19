from ..repositories.RolRepository import select_all


def select_all_rol_service():
    roles = select_all()
    print (roles)
    return roles