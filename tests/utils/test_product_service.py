# tests/utils/test_product_service.py
"""
Tests para services/ProductService.py
--------------------------------------
Se simulan llamadas a repositorios para evitar acceso real a la BD.
"""

from types import SimpleNamespace as NS
import pytest

import della_soft.services.ProductService as psvc


# ------------------------------------------------------------------
# select_all_product_service
# ------------------------------------------------------------------
def test_select_all_product_service(monkeypatch):
    monkeypatch.setattr(psvc, "select_all", lambda: ["P1", "P2"])
    result = psvc.select_all_product_service()
    assert result == ["P1", "P2"]


# ------------------------------------------------------------------
# select_product – con valor
# ------------------------------------------------------------------
def test_select_product_with_value(monkeypatch):
    monkeypatch.setattr(psvc, "get_product", lambda val: f"PRODUCT:{val}")
    result = psvc.select_product("ABC123")
    assert result == "PRODUCT:ABC123"


# ------------------------------------------------------------------
# select_product – sin valor
# ------------------------------------------------------------------
def test_select_product_empty(monkeypatch):
    monkeypatch.setattr(psvc, "select_all", lambda: ["ALL_PRODUCTS"])
    result = psvc.select_product("")
    assert result == ["ALL_PRODUCTS"]


# ------------------------------------------------------------------
# create_product – debe construir un Product y pasarlo a insert
# ------------------------------------------------------------------
def test_create_product(monkeypatch):
    captured = {}

    def fake_insert_product(product_obj):
        captured["product"] = product_obj
        return "CREATED"

    monkeypatch.setattr(psvc, "insert_product", fake_insert_product)

    result = psvc.create_product(
        id=1,
        name="Test",
        description="Test product",
        product_type="Precio Por Kilo",
        price=10000
    )

    assert result == "CREATED"
    p = captured["product"]
    assert p.id == 1
    assert p.name == "Test"
    assert p.product_type == "Precio Por Kilo"
    assert p.price == 10000


# ------------------------------------------------------------------
# delete_product_service – passthrough
# ------------------------------------------------------------------
def test_delete_product_service(monkeypatch):
    monkeypatch.setattr(psvc, "delete_product", lambda pid: f"DELETED:{pid}")
    result = psvc.delete_product_service(5)
    assert result == "DELETED:5"


# ------------------------------------------------------------------
# update_product_service – construye y pasa Product a update
# ------------------------------------------------------------------
def test_update_product_service(monkeypatch):
    captured = {}

    def fake_update_product(product_obj):
        captured["product"] = product_obj

    monkeypatch.setattr(psvc, "update_product", fake_update_product)

    result = psvc.update_product_service(
        id=7,
        name="Updated",
        description="Updated Desc",
        product_type="Precio Por Kilo",
        price=2000
    )

    assert result.id == 7
    assert result.name == "Updated"
    assert result.product_type == "Precio Por Kilo"
    assert result.price == 2000
    assert captured["product"] == result