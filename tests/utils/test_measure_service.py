"""
Tests para services/MeasureService.py
-------------------------------------
Se usan monkeypatches para aislar los llamados al repositorio.
"""

from types import SimpleNamespace as NS
import pytest

import della_soft.services.MeasureService as ms


# -----------------------------------------------------------------
#  select_all_measure_service   (pasa-through)
# -----------------------------------------------------------------
def test_select_all(monkeypatch):
    fake_rows = [NS(id=1), NS(id=2)]
    monkeypatch.setattr(ms, "select_all", lambda: fake_rows)

    out = ms.select_all_measure_service()
    assert out == fake_rows


# -----------------------------------------------------------------
#  select_name_by_id  (rama éxito)
# -----------------------------------------------------------------
def test_select_name_by_id_ok(monkeypatch):
    monkeypatch.setattr(ms, "select_by_id",
                        lambda _id: [NS(id=_id, description="Kg")] if _id == 3 else [])

    assert ms.select_name_by_id(3) == "Kg"


# -----------------------------------------------------------------
#  select_name_by_id  (rama error)
# -----------------------------------------------------------------
def test_select_name_by_id_not_found(monkeypatch):
    monkeypatch.setattr(ms, "select_by_id", lambda _id: [])

    with pytest.raises(ValueError):
        ms.select_name_by_id(99)