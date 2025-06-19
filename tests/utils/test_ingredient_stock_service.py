"""
Tests para services/IngredientStockService.py
---------------------------------------------
Todos los accesos al repositorio se falsifican con monkeypatch
para aislar la lógica del servicio.
"""

from types import SimpleNamespace as NS

import pytest

import della_soft.services.IngredientStockService as iss


# -----------------------------------------------------------------
#  async backend – usamos sólo asyncio
# -----------------------------------------------------------------
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


# -----------------------------------------------------------------
#  select_all_stock_service   (pasa-through)
# -----------------------------------------------------------------
@pytest.mark.anyio
async def test_select_all_stock(monkeypatch):
    fake_rows = [NS(id=1), NS(id=2)]
    monkeypatch.setattr(iss, "select_all", lambda: fake_rows)

    out = await iss.select_all_stock_service()
    assert out == fake_rows


# -----------------------------------------------------------------
#  insert_ingredient_stock_service
# -----------------------------------------------------------------
@pytest.mark.anyio
async def test_insert_stock(monkeypatch):
    captured = {}

    def _insert(row):
        captured["row"] = row
        return "OK"

    monkeypatch.setattr(iss, "insert_stock", _insert)

    res = await iss.insert_ingredient_stock_service(ing_id := 7, qty := 3.5, min_q := 1.0)
    assert res == "OK"

    row = captured["row"]
    assert row.ingredient_id == ing_id
    assert row.quantity == qty
    assert row.min_quantity == min_q


# -----------------------------------------------------------------
#  update_ingredient_stock_service   (args pasan intactos)
# -----------------------------------------------------------------
@pytest.mark.anyio
async def test_update_stock(monkeypatch):
    captured = {}

    def _update(stock_id, q, min_q):
        captured.update(id=stock_id, q=q, min_q=min_q)
        return "UPDATED"

    monkeypatch.setattr(iss, "update_stock", _update)

    res = await iss.update_ingredient_stock_service(5, 10.0, 2.0)
    assert res == "UPDATED"
    assert captured == {"id": 5, "q": 10.0, "min_q": 2.0}
