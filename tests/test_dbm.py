import pytest

from ecalc import calc
from ecalc.cli import main


@pytest.mark.parametrize("dbm,mw", [(0, 1), (10, 10), (20, 100), (30, 1000), (-10, 0.1)])
def test_dbm_to_mw(dbm, mw):
    assert calc.dbm_to_mw(dbm) == pytest.approx(mw)


@pytest.mark.parametrize("dbm,mw", [(0, 1), (10, 10), (30, 1000), (-30, 0.001)])
def test_mw_to_dbm(dbm, mw):
    assert calc.mw_to_dbm(mw) == pytest.approx(dbm)


def test_round_trip():
    assert calc.mw_to_dbm(calc.dbm_to_mw(13.37)) == pytest.approx(13.37)


@pytest.mark.parametrize("mw", [0, -5])
def test_non_positive_mw_rejected(mw):
    with pytest.raises(ValueError):
        calc.mw_to_dbm(mw)


def test_cli_dbm_to_mw(capsys):
    main(["dbm", "--dbm", "20"])
    assert capsys.readouterr().out.strip() == "20 dBm = 100 mW"


def test_cli_mw_to_dbm(capsys):
    main(["dbm", "--mw", "1000"])
    assert capsys.readouterr().out.strip() == "1000 mW = 30 dBm"


def test_cli_requires_exactly_one_option():
    with pytest.raises(SystemExit):
        main(["dbm"])
    with pytest.raises(SystemExit):
        main(["dbm", "--dbm", "1", "--mw", "1"])
