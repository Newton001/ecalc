import pytest

from ecalc import calc
from ecalc.cli import main


def test_equal_resistors_halve_voltage():
    assert calc.divider(10, 1000, 1000) == pytest.approx(5.0)


def test_unequal_resistors():
    assert calc.divider(12, 10_000, 4_700) == pytest.approx(12 * 4700 / 14700)


def test_r2_zero_gives_zero():
    assert calc.divider(5, 1000, 0) == 0


@pytest.mark.parametrize("r1,r2", [(0, 0), (-1, 100), (100, -1)])
def test_invalid_resistances(r1, r2):
    with pytest.raises(ValueError):
        calc.divider(5, r1, r2)


def test_cli_output(capsys):
    assert main(["divider", "5", "1000", "1000"]) == 0
    assert capsys.readouterr().out.strip() == "Vout = 2.5 V"


def test_cli_error_exits_2(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["divider", "5", "0", "0"])
    assert exc.value.code == 2
    assert "R1 + R2" in capsys.readouterr().err
