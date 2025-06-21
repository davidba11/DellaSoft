# tests/utils/test_product_order_service.py
"""
Tests para services/ProductOrderService.py
-------------------------------------------
Se simula el acceso a base de datos mediante monkey-patches.
"""

import pytest
from types import SimpleNamespace as NS

import della_soft.services.ProductOrderService as posvc

# No requiere async


# ------------------------------------------------------------------
# select_all_product_order_service
# ------------------------------------------------------------------
def test_select_all_product_order(monkeypatch):
    monkeypatch.setattr(posvc, "select_all", lambda: ["P1", "P2"])
    result = posvc.select_all_product_order_service()
    assert result == ["P1", "P2"]


# ------------------------------------------------------------------
# select_by_order_id_service
# ------------------------------------------------------------------
def test_select_by_order_id(monkeypatch):
    monkeypatch.setattr(posvc, "select_by_order_id", lambda oid: f"ORDER_{oid}")
    result = posvc.select_by_order_id_service(123)
    assert result == "ORDER_123"


# ------------------------------------------------------------------
# get_fixed_products_by_order_id
# ------------------------------------------------------------------
def test_get_fixed_products_by_order_id(monkeypatch):
    monkeypatch.setattr(posvc, "select_fixed_products", lambda oid: [f"FIXED_{oid}"])
    result = posvc.get_fixed_products_by_order_id(456)
    assert result == ["FIXED_456"]


# ------------------------------------------------------------------
# insert_product_order_service
# ------------------------------------------------------------------
def test_insert_product_order_service(monkeypatch):
    captured = {}

    def fake_insert(po):
        captured["product_order"] = po
        return "INSERTED"

    monkeypatch.setattr(posvc, "insert_repo_product_order", fake_insert)

    fake_order = NS(id=1, name="FakeProduct")
    result = posvc.insert_product_order_service(fake_order)

    assert result == "INSERTED"
    assert captured["product_order"] == fake_order


# ------------------------------------------------------------------
# delete_product_order_service
# ------------------------------------------------------------------
def test_delete_product_order_service(monkeypatch):
    monkeypatch.setattr(posvc, "delete_product_order", lambda pid: f"DELETED:{pid}")
    result = posvc.delete_product_order_service(99)
    assert result == "DELETED:99"


# ------------------------------------------------------------------
# update_product_orders – elimina los existentes e inserta los nuevos
# ------------------------------------------------------------------
def test_update_product_orders(monkeypatch):
    called = {"deleted": [], "inserted": []}

    def fake_select_by_order_id(oid):
        return [NS(id=1), NS(id=2)]

    def fake_delete_product_order(pid):
        called["deleted"].append(pid)

    def fake_insert_product_order(po):
        called["inserted"].append(po)

    monkeypatch.setattr(posvc, "select_by_order_id", fake_select_by_order_id)
    monkeypatch.setattr(posvc, "delete_product_order", fake_delete_product_order)
    monkeypatch.setattr(posvc, "insert_product_order", fake_insert_product_order)

    new_orders = [NS(id=3), NS(id=4)]
    posvc.update_product_orders(order_id=1, new_product_orders=new_orders)

    assert called["deleted"] == [1, 2]
    assert called["inserted"] == new_orders