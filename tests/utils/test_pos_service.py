# tests/utils/test_pos_service.py
"""
Tests para services/POSService.py
----------------------------------
Se utilizan monkey-patches para simular acceso al repositorio
y evitar operaciones reales con la base de datos.
"""

from datetime import datetime
import pytest
from types import SimpleNamespace as NS

import della_soft.services.POSService as psvc

# No se necesita asyncio porque no hay funciones async


# ------------------------------------------------------------------
# pos_is_open – llama a get_by_pos_date con el parámetro correcto
# ------------------------------------------------------------------
def test_pos_is_open(monkeypatch):
    called = {}

    def fake_get_by_pos_date(value):
        called["value"] = value
        return "POS_RESULT"

    monkeypatch.setattr(psvc, "get_by_pos_date", fake_get_by_pos_date)

    result = psvc.pos_is_open("2025-06-19")
    assert result == "POS_RESULT"
    assert called["value"] == "2025-06-19"


# ------------------------------------------------------------------
# insert_pos_register – construye POS correctamente y llama a insert
# ------------------------------------------------------------------
def test_insert_pos_register(monkeypatch):
    captured = {}

    def fake_insert_pos(pos_obj):
        captured["pos"] = pos_obj

    monkeypatch.setattr(psvc, "insert_pos", fake_insert_pos)

    psvc.insert_pos_register(
        id=1,
        initial_amount=5000,
        final_amount=0,
        pos_date=datetime(2025, 6, 19, 8, 0)
    )

    pos = captured["pos"]
    assert pos.id == 1
    assert pos.initial_amount == 5000
    assert pos.final_amount == 0
    assert pos.pos_date == datetime(2025, 6, 19, 8, 0)


# ------------------------------------------------------------------
# update_final_amount – construye POS correctamente y llama a update
# ------------------------------------------------------------------
def test_update_final_amount(monkeypatch):
    captured = {}

    def fake_update_pos(pos_obj):
        captured["pos"] = pos_obj

    monkeypatch.setattr(psvc, "update_pos", fake_update_pos)

    psvc.update_final_amount(
        id=2,
        initial_amount=8000,
        final_amount=12000,
        pos_date=datetime(2025, 6, 19, 18, 0)
    )

    pos = captured["pos"]
    assert pos.id == 2
    assert pos.initial_amount == 8000
    assert pos.final_amount == 12000
    assert pos.pos_date == datetime(2025, 6, 19, 18, 0)