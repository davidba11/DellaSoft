"""
Tests para services/IngredientService.py
----------------------------------------
• Todas las dependencias del repositorio se “monkey-patchean”.
• Se usa cualquier objeto-dummy (types.SimpleNamespace) en lugar del
  modelo real Ingredient – es suficiente para validar la lógica.
"""

from types import SimpleNamespace as NS

import pytest

import della_soft.services.IngredientService as isvc


# -----------------------------------------------------------------
#  async backend: sólo asyncio  →  evita que anyio busque trio
# -----------------------------------------------------------------
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


# -----------------------------------------------------------------
#  select_all_ingredient_service
# -----------------------------------------------------------------
@pytest.mark.anyio
async def test_select_all(monkeypatch):
    fake = [NS(id=1), NS(id=2)]
    monkeypatch.setattr(isvc, "select_all", lambda: fake)

    out = await isvc.select_all_ingredient_service()
    assert out == fake


# -----------------------------------------------------------------
#  select_ingredient_service: rama “value vacío”  (debe llamar select_all)
# -----------------------------------------------------------------
@pytest.mark.anyio
async def test_select_ingredient_empty(monkeypatch):
    called = {"all": False}

    def _select_all():
        called["all"] = True
        return ["ALL"]

    monkeypatch.setattr(isvc, "select_all", _select_all)
    monkeypatch.setattr(isvc, "get_ingredient", lambda v: ["NEVER"])

    out = await isvc.select_ingredient_service("")
    assert out == ["ALL"]
    assert called["all"] is True


# -----------------------------------------------------------------
#  select_ingredient_service: rama con value  (debe llamar get_ingredient)
# -----------------------------------------------------------------
@pytest.mark.anyio
async def test_select_ingredient_with_value(monkeypatch):
    monkeypatch.setattr(isvc, "select_all",  lambda: ["BAD"])
    monkeypatch.setattr(isvc, "get_ingredient", lambda v: [f"ING:{v}"])

    out = await isvc.select_ingredient_service("Azúcar")
    assert out == ["ING:Azúcar"]


# -----------------------------------------------------------------
#  create_ingredient → se construye objeto y se pasa a insert_ingredient
# -----------------------------------------------------------------
def test_create_ingredient(monkeypatch):
    captured = {}

    def _insert_ing(obj):
        # guardamos la referencia para las aserciones
        captured["obj"] = obj
        return "OK"

    monkeypatch.setattr(isvc, "insert_ingredient", _insert_ing)

    res = isvc.create_ingredient(9, "Harina", 3)
    assert res == "OK"

    obj = captured["obj"]
    assert obj.id == 9
    assert obj.name == "Harina"
    assert obj.measure_id == 3


# -----------------------------------------------------------------
#  update_ingredient_service → pasa-through
# -----------------------------------------------------------------
def test_update_ingredient(monkeypatch):
    dummy = NS(id=1, name="X")

    monkeypatch.setattr(isvc, "update_ingredient", lambda ing: ("UPDATED", ing))

    out = isvc.update_ingredient_service(dummy)
    assert out == ("UPDATED", dummy)