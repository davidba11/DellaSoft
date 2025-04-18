from ..repositories.RolRepository import select_all


def select_all_roles_service():
    roles = select_all()
    print (roles)
    return roles