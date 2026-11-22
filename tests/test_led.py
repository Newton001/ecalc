import math

import pytest

from ecalc import calc
from ecalc.cli import main


@pytest.mark.parametrize(
    "ohms,expected",
    [
        (150, 150),          # exact E12 value is kept
        (151, 180),
        (86.667, 100),       # rolls over into the next decade
        (880, 1000),
        (1, 1),
        (0.5, 0.56),
        (4701, 5600),
        (8200, 8200),
        (8201, 10000),
        (1_000_000, 1_000_000),
    ],
)
def test_e12_ceil(ohms, expected):
    assert calc.e12_ceil(ohms) == pytest.approx(expected)


def test_e12_ceil_every_value_maps_to_itself():
    for exp in range(-2, 7):
        for v in calc.E12:
            r = v * 10 ** exp
            assert calc.e12_ceil(r) == pytest.approx(r)


@pytest.mark.parametrize("ohms", [0, -10, math.inf, math.nan])
def test_e12_ceil_invalid(ohms):
    with pytest.raises(ValueError):
        calc.e12_ceil(ohms)


def test_led_exact_value():
    ideal, r, ma, watts = calc.led(5, 2, 20)
    assert ideal == pytest.approx(150)
    assert r == 150
    assert ma == pytest.approx(20)
    assert watts == pytest.approx(0.06)


def test_led_rounds_up_and_recomputes_power():
    ideal, r, ma, watts = calc.led(12, 3.2, 10)
    assert ideal == pytest.approx(880)
    assert r == 1000
    assert ma == pytest.approx(8.8)
    assert watts == pytest.approx(8.8 ** 2 / 1000)


def test_led_current_never_exceeds_target():
    for vs in (3.3, 5, 9, 12, 24):
        for ma in (1, 2, 5, 10, 15, 20, 30):
            _, _, actual, _ = calc.led(vs, 2.0, ma)
            assert actual <= ma * (1 + 1e-9)


@pytest.mark.parametrize(
    "vs,vf,ma,msg",
    [
        (2, 2, 20, "greater than the LED forward voltage"),
        (1.5, 2, 20, "greater than the LED forward voltage"),
        (5, 0, 20, "forward voltage must be greater than zero"),
        (5, -1, 20, "forward voltage must be greater than zero"),
        (5, 2, 0, "current must be greater than zero"),
        (5, 2, -5, "current must be greater than zero"),
        (math.nan, 2, 20, "finite"),
        (math.inf, 2, 20, "finite"),
        (5, 2, math.inf, "finite"),
    ],
)
def test_led_invalid(vs, vf, ma, msg):
    with pytest.raises(ValueError, match=msg):
        calc.led(vs, vf, ma)


def test_cli_output(capsys):
    assert main(["led", "12", "3.2", "10"]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out == [
        "R = 1 kΩ (E12; calculated 880 Ω)",
        "I = 8.8 mA, P = 77.44 mW",
    ]


def test_cli_error_exits_2(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["led", "3", "3.2", "20"])
    assert exc.value.code == 2
    assert "forward voltage" in capsys.readouterr().err


def test_cli_non_numeric_rejected():
    with pytest.raises(SystemExit):
        main(["led", "five", "2", "20"])
