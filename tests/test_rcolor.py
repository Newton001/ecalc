import pytest

from ecalc import calc
from ecalc.cli import main


@pytest.mark.parametrize(
    "bands,ohms,tol",
    [
        (["brown", "black", "red", "gold"], 1000, 5),
        (["yellow", "violet", "red", "gold"], 4700, 5),
        (["red", "red", "brown", "silver"], 220, 10),
        (["brown", "black", "black", "brown"], 10, 1),
        (["green", "blue", "gold", "red"], 5.6, 2),
        (["orange", "orange", "silver", "gold"], 0.33, 5),
        (["blue", "grey", "yellow", "green"], 680_000, 0.5),
        (["brown", "black", "blue", "violet"], 10_000_000, 0.1),
    ],
)
def test_decode(bands, ohms, tol):
    value, tolerance = calc.rcolor(bands)
    assert value == pytest.approx(ohms)
    assert tolerance == tol


def test_case_and_aliases():
    assert calc.rcolor(["Brown", "GRAY", "Red", "Gold"]) == (1800, 5)
    assert calc.rcolor(["purple", "black", "black", "gold"]) == (70, 5)


@pytest.mark.parametrize(
    "bands",
    [
        ["gold", "black", "red", "gold"],     # gold isn't a digit
        ["brown", "black", "pink", "gold"],   # unknown multiplier
        ["brown", "black", "red", "black"],   # black isn't a tolerance
        ["brown", "black", "red"],            # too few bands
    ],
)
def test_invalid_bands(bands):
    with pytest.raises(ValueError):
        calc.rcolor(bands)


@pytest.mark.parametrize(
    "ohms,text",
    [(0.33, "0.33 Ω"), (220, "220 Ω"), (4700, "4.7 kΩ"), (1_000_000, "1 MΩ")],
)
def test_format_ohms(ohms, text):
    assert calc.format_ohms(ohms) == text


def test_cli_output(capsys):
    main(["rcolor", "yellow", "violet", "red", "gold"])
    assert capsys.readouterr().out.strip() == "4.7 kΩ ±5%"


def test_cli_invalid_colour(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["rcolor", "brown", "black", "red", "pink"])
    assert exc.value.code == 2
    assert "invalid tolerance colour 'pink'" in capsys.readouterr().err
