"""
Pruebas unitarias para CustomerService.py

Se stubbean (simulan) todas las dependencias de acceso a BD para
validar únicamente la lógica de branching y la construcción de objetos
que hace la capa *service*.
"""
from types import SimpleNamespace as NS
from datetime import datetime
import pytest

# Módulo bajo prueba
from della_soft.services import CustomerService as cs
# Alias del modelo (solo para asserts de tipo)
from della_soft.models.CustomerModel import Customer


# ---------------------------------------------------------------------------
# FIXTURE GLOBAL: obliga a pytest-anyio a usar asyncio → evitamos trio
# ---------------------------------------------------------------------------
@pytest.fixture
def anyio_backend():
    return "asyncio"


# ---------------------------------------------------------------------------
# HELPERS / STUBS
# ---------------------------------------------------------------------------
def _fake_customer(pk=1, first="Foo", last="Bar") -> Customer:
    """Construye un Customer de prueba."""
    return Customer(id=pk, first_name=first, last_name=last, ci="1",
                    contact="123", id_rol=2)

def _fake_create(cust: Customer):
    """Devuelve exactamente el objeto recibido (para las asserts)."""
    return cust


# ---------------------------------------------------------------------------
# TESTS: funciones que actúan como simples proxies
# ---------------------------------------------------------------------------
def test_select_all_proxy(monkeypatch):
    monkeypatch.setattr(cs, "select_all", lambda: ["ALL"])
    assert cs.select_all_customer_service() == ["ALL"]


def test_select_all_users_proxy(monkeypatch):
    monkeypatch.setattr(cs, "select_all_users", lambda: ["U_ALL"])
    assert cs.select_all_users_service() == ["U_ALL"]


# ---------------------------------------------------------------------------
# Branching: con / sin parámetro de búsqueda
# ---------------------------------------------------------------------------
def test_select_by_parameter_branching(monkeypatch):
    monkeypatch.setattr(cs, "select_by_parameter",
                        lambda val: [f"PARAM:{val}"])
    monkeypatch.setattr(cs, "select_all", lambda: ["ALL"])

    # con texto
    assert cs.select_by_parameter_service("abc") == ["PARAM:abc"]
    # vacío → recae a select_all
    assert cs.select_by_parameter_service("  ") == ["ALL"]


def test_select_users_by_parameter_branching(monkeypatch):
    monkeypatch.setattr(cs, "select_users_by_parameter",
                        lambda val: [f"U_PARAM:{val}"])
    monkeypatch.setattr(cs, "select_all_users", lambda: ["U_ALL"])

    assert cs.select_users_by_parameter_service("xyz") == ["U_PARAM:xyz"]
    assert cs.select_users_by_parameter_service("") == ["U_ALL"]


# ---------------------------------------------------------------------------
# select_name_by_id
# ---------------------------------------------------------------------------
def test_select_name_by_id_ok(monkeypatch):
    monkeypatch.setattr(cs, "select_by_id", lambda pk: [_fake_customer(pk)])
    full = cs.select_name_by_id(7)
    assert full == "Foo Bar"


def test_select_name_by_id_not_found(monkeypatch):
    monkeypatch.setattr(cs, "select_by_id", lambda pk: [])
    with pytest.raises(ValueError):
        cs.select_name_by_id(99)


# ---------------------------------------------------------------------------
# create_user_service  (feliz y error por ID duplicado)
# ---------------------------------------------------------------------------
def test_create_user_ok(monkeypatch):
    # No hay usuario existente ⇒ select_by_id_service devuelve lista vacía
    monkeypatch.setattr(cs, "select_by_id_service", lambda _: [])
    monkeypatch.setattr(cs, "create_user", _fake_create)

    out = cs.create_user_service(
        "Ana", "Diaz", "555", "ana", "123", 2, "123456"
    )
    assert isinstance(out, Customer)
    assert out.first_name == "Ana"
    assert out.id_rol == 2


def test_create_user_duplicate_id(monkeypatch):
    monkeypatch.setattr(
        cs, "select_by_id_service", lambda _id: [_fake_customer(pk=_id)]
    )
    with pytest.raises(ValueError):
        cs.create_user_service("A", "B", "C", "u", "p", 1, "ci", id=1)


# ---------------------------------------------------------------------------
# update_customer_service  (simple smoke test del wrapper)
# ---------------------------------------------------------------------------
def test_update_customer_service(monkeypatch):
    saved = {}
    def _fake_update(cust): saved["obj"] = cust
    monkeypatch.setattr(cs, "update_customer", _fake_update)

    out = cs.update_customer_service(id=10, first_name="Zoe", last_name="X",
                                     ci="9", contact="0", id_rol=2)
    assert saved["obj"].id == 10
    assert out.last_name == "X"


# ---------------------------------------------------------------------------
# get_customer_id_by_name_service (async)
# ---------------------------------------------------------------------------
@pytest.mark.anyio
async def test_get_customer_id_by_name_async_ok(monkeypatch):
    async def _fake_sel(name):
        return NS(id=42) if name == "Foo" else None

    monkeypatch.setattr(cs, "select_by_name", _fake_sel)

    assert await cs.get_customer_id_by_name_service("Foo") == 42


@pytest.mark.anyio
async def test_get_customer_id_by_name_async_fail(monkeypatch):
    async def _fake_none(_):
        return None

    monkeypatch.setattr(cs, "select_by_name", _fake_none)

    with pytest.raises(ValueError):
        await cs.get_customer_id_by_name_service("Quien?")
