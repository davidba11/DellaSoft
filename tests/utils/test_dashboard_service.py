"""
Tests for della_soft.services.DashboardService

• Fecha fija 15-05-2025.
• Repositorios stub in-memory.
• Sólo backend asyncio (fixture anyio_backend).
"""
from __future__ import annotations

from datetime import date, timedelta
from types import SimpleNamespace as NS

import pytest

import della_soft.services.DashboardService as ds


# ------------------------------------------------------------------
# 使 pytest-anyio use únicamente asyncio (evita “trio”)
# ------------------------------------------------------------------
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


# ------------------------------------------------------------------
# Congelamos date.today() → 15-05-2025
# ------------------------------------------------------------------
class _FakeToday(date):
    @classmethod
    def today(cls):  # noqa: D401,N802  (override API stdlib)
        return cls(2025, 5, 15)


def _patch_today(monkeypatch):
    monkeypatch.setattr(ds, "date", _FakeToday)


# ------------------------------------------------------------------
# get_stock_rotation_data_month
# ------------------------------------------------------------------
@pytest.mark.anyio
async def test_stock_rotation(monkeypatch):
    _patch_today(monkeypatch)

    prods   = [NS(id=1, name="Café"), NS(id=2, name="Té")]
    stocks  = [NS(product_id=1, quantity=20), NS(product_id=2, quantity=5)]
    porders = [
        NS(id_product=1, id_order=101, quantity=3),   # mayo
        NS(id_product=1, id_order=102, quantity=1),   # abril
    ]
    orders  = [
        NS(id=101, order_date=date(2025, 5, 10)),
        NS(id=102, order_date=date(2025, 4, 20)),
    ]

    monkeypatch.setattr(ds, "select_all_products", lambda: prods)
    monkeypatch.setattr(ds, "select_all_product_stocks", lambda: stocks)
    monkeypatch.setattr(ds, "select_all_product_orders", lambda: porders)

    async def _fake_orders():
        return orders

    monkeypatch.setattr(ds, "select_all_orders", _fake_orders)

    out = await ds.get_stock_rotation_data_month()
    cafe, te = out

    assert cafe["Producto"] == "Café"
    assert cafe["Stock Disponible"] == 20
    assert cafe["Cantidad Vendida (Rotación)"] == 3          # solo mayo

    assert te["Producto"] == "Té"
    assert te["Stock Disponible"] == 5
    assert te["Cantidad Vendida (Rotación)"] == 0            # no ventas en mayo


# ------------------------------------------------------------------
# get_top_products_month
# ------------------------------------------------------------------
@pytest.mark.anyio
async def test_top_products(monkeypatch):
    _patch_today(monkeypatch)

    prods = [NS(id=i, name=f"P{i}") for i in range(1, 6)]
    porders = [
        NS(id_product=1, id_order=1, quantity=10),   # mayo
        NS(id_product=2, id_order=1, quantity=5),    # mayo
        NS(id_product=3, id_order=2, quantity=7),    # mayo
        NS(id_product=4, id_order=3, quantity=1),    # abril (fuera)
    ]
    orders = [
        NS(id=1, order_date=date(2025, 5, 1)),
        NS(id=2, order_date=date(2025, 5, 2)),
        NS(id=3, order_date=date(2025, 4, 30)),
    ]

    monkeypatch.setattr(ds, "select_all_products", lambda: prods)
    monkeypatch.setattr(ds, "select_all_product_orders", lambda: porders)

    async def _fake_orders():
        return orders

    monkeypatch.setattr(ds, "select_all_orders", _fake_orders)

    top = await ds.get_top_products_month()
    nombres = [r["Producto"] for r in top]

    assert nombres == ["P1", "P3", "P2", "P4", "P5"][: len(top)]
    assert top[0]["Cantidad Vendida"] == 10                # P1
    assert top[-1]["Cantidad Vendida"] == 0                # P5 sin ventas


# ------------------------------------------------------------------
# get_orders_per_day_month
# ------------------------------------------------------------------
@pytest.mark.anyio
async def test_orders_per_day(monkeypatch):
    _patch_today(monkeypatch)

    base = date(2025, 5, 1)

    def make_order(oid, day_offset):
        return NS(id=oid, order_date=base + timedelta(days=day_offset))

    orders = [
        make_order(1, 0),   # 01/05
        make_order(2, 0),   # 01/05 (otro)
        make_order(3, 2),   # 03/05
        make_order(4, 14),  # 15/05
    ]

    async def _fake_orders():
        return orders

    monkeypatch.setattr(ds, "select_all_orders", _fake_orders)

    per_day = await ds.get_orders_per_day_month()
    dic = {row["Fecha"]: row["Pedidos"] for row in per_day}

    assert dic["01/05"] == 2
    assert dic["03/05"] == 1
    assert dic["15/05"] == 1
    # Día sin pedidos debe reportar 0
    assert dic["10/05"] == 0
