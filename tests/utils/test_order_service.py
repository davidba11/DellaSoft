# tests/utils/test_order_service.py
"""
Tests para services/OrderService.py
-----------------------------------
Se emplean monkey-patches para aislar la lógica del repositorio
y evitar accesos reales a BD.
"""

from types import SimpleNamespace as NS
from datetime import datetime
import pytest

import della_soft.services.OrderService as osvc


# ──────────────────────────────────────────────────────────────
# ▶️  Forzamos backend asyncio para todo este archivo
pytestmark = pytest.mark.anyio
# ──────────────────────────────────────────────────────────────


# ------------------------------------------------------------------
# select_all_order_service  (async passthrough)
# ------------------------------------------------------------------
async def test_select_all_order_async_ok(monkeypatch):
    fake_rows = [NS(id=1), NS(id=2)]

    async def _fake_select_all():
        return fake_rows

    monkeypatch.setattr(osvc, "select_all", _fake_select_all)

    out = await osvc.select_all_order_service()
    assert out == fake_rows


# ------------------------------------------------------------------
# select_order – rama con parámetro
# ------------------------------------------------------------------
def test_select_order_with_value(monkeypatch):
    monkeypatch.setattr(osvc, "get_order", lambda val: [f"ORDER:{val}"])
    out = osvc.select_order("ABC123")
    assert out == ["ORDER:ABC123"]


# ------------------------------------------------------------------
# select_order – rama sin parámetro
# ------------------------------------------------------------------
def test_select_order_empty(monkeypatch):
    monkeypatch.setattr(osvc, "select_all", lambda: ["ALL"])
    out = osvc.select_order("")
    assert out == ["ALL"]


# ------------------------------------------------------------------
# create_order devuelve lo que retorna insert_order
# ------------------------------------------------------------------
def test_create_order_pass_object(monkeypatch):
    captured = {}

    def _fake_insert(order_obj):
        captured["obj"] = order_obj
        return "CREATED"

    monkeypatch.setattr(osvc, "insert_order", _fake_insert)

    result = osvc.create_order(
        id=10,
        id_customer=5,
        observation="Obs",
        total_order="100",
        total_paid="0",
        order_date=datetime(2025, 1, 1, 12, 0),
        delivery_date=datetime(2025, 1, 2),
    )

    # retorna lo que devuelve el repo
    assert result == "CREATED"

    # El objeto que llega al repositorio contiene los datos correctos
    obj = captured["obj"]
    assert obj.id == 10 and obj.id_customer == 5
    assert int(obj.total_order) == 100
    assert int(obj.total_paid) == 0


# ------------------------------------------------------------------
# update_order_service / update_pay_amount_service – passthrough
# ------------------------------------------------------------------
def test_update_order_passthrough(monkeypatch):
    monkeypatch.setattr(osvc, "update_order", lambda o: "UPDATED")
    assert osvc.update_order_service(NS()) == "UPDATED"


def test_update_pay_amount_passthrough(monkeypatch):
    monkeypatch.setattr(osvc, "update_pay_amount", lambda o: "UPDATED$")
    assert osvc.update_pay_amount_service(NS()) == "UPDATED$"