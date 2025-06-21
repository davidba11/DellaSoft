import re
from datetime import datetime, timedelta

import pytest

from della_soft.services import SystemService as ss


# ------------------------------------------------------------------
# Funciones que devuelven strings de fecha
# ------------------------------------------------------------------
def test_get_sys_date_to_string_format():
    """
    Asegura que el formato sea DD/MM/YYYY HH:MM
    (no validamos la hora exacta porque pasa muy rápido en CI).
    """
    date_str = ss.get_sys_date_to_string()
    assert re.fullmatch(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}", date_str)


def test_get_sys_date_to_string_two_format():
    """
    Formato DD/MM/YYYY (sin hora).
    """
    date_str = ss.get_sys_date_to_string_two()
    assert re.fullmatch(r"\d{2}/\d{2}/\d{4}", date_str)


# ------------------------------------------------------------------
# Hash + verificación de contraseña
# ------------------------------------------------------------------
def test_hash_and_verify_password():
    pwd = "SúperSecreta123!"
    hashed = ss.hash_password(pwd)

    assert hashed != pwd           # nunca debe ser texto plano
    assert ss.verify_password(pwd, hashed) is True
    assert ss.verify_password("otra", hashed) is False


# ------------------------------------------------------------------
# Conversión de strings a datetime
# ------------------------------------------------------------------
@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("2025-05-19T14:30", datetime(2025, 5, 19, 14, 30)),
        ("2025-05-19 14:30:00", datetime(2025, 5, 19, 14, 30)),
        ("19/05/2025 14:30", datetime(2025, 5, 19, 14, 30)),
    ],
)
def test_get_sys_date_parses_multiple_formats(input_str, expected):
    assert ss.get_sys_date(input_str) == expected


def test_get_sys_date_invalid_format():
    with pytest.raises(ValueError):
        ss.get_sys_date("19-05-2025")   # formato no soportado


def test_get_sys_date_two():
    dt = ss.get_sys_date_two("01/01/2030")
    assert dt == datetime(2030, 1, 1)


def test_get_sys_date_three_midnight():
    dt = ss.get_sys_date_three("02/01/2030")
    assert dt == datetime(2030, 1, 2, 0, 0)