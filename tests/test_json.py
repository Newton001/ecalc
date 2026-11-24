"""Tests for the --json flag on every subcommand."""

import json

import pytest

from ecalc.cli import main


def run_json(capsys, argv):
    assert main(argv) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    return json.loads(captured.out)


def test_divider_json(capsys):
    data = run_json(capsys, ["divider", "--json", "12", "10000", "4700"])
    assert set(data) == {"vin", "r1", "r2", "vout"}
    assert data["vin"] == 12 and data["r1"] == 10000 and data["r2"] == 4700
    assert data["vout"] == pytest.approx(12 * 4700 / 14700)


def test_json_flag_position_is_flexible(capsys):
    first = run_json(capsys, ["divider", "--json", "5", "1000", "1000"])
    last = run_json(capsys, ["divider", "5", "1000", "1000", "--json"])
    assert first == last == {"vin": 5, "r1": 1000, "r2": 1000, "vout": 2.5}


def test_dbm_to_mw_json(capsys):
    assert run_json(capsys, ["dbm", "--json", "--dbm", "20"]) == pytest.approx(
        {"dbm": 20, "mw": 100}
    )


def test_mw_to_dbm_json(capsys):
    assert run_json(capsys, ["dbm", "--mw", "0.5", "--json"]) == pytest.approx(
        {"dbm": -3.0103, "mw": 0.5}, abs=1e-4
    )


def test_rcolor_json(capsys):
    data = run_json(capsys, ["rcolor", "--json", "Yellow", "purple", "red", "gold"])
    assert data == {
        "bands": ["yellow", "violet", "red", "gold"],
        "ohms": 4700,
        "tolerance_percent": 5,
        "formatted": "4.7 kΩ ±5%",
    }


def test_led_json(capsys):
    data = run_json(capsys, ["led", "--json", "12", "3.2", "10"])
    assert set(data) == {
        "vsupply", "vf", "target_ma", "ideal_ohms", "ohms", "ma", "power_mw"
    }
    assert data["vsupply"] == 12 and data["vf"] == 3.2 and data["target_ma"] == 10
    assert data["ideal_ohms"] == pytest.approx(880)
    assert data["ohms"] == pytest.approx(1000)
    assert data["ma"] == pytest.approx(8.8)
    assert data["power_mw"] == pytest.approx(77.44)


def test_led_json_exact_e12_value(capsys):
    assert run_json(capsys, ["led", "5", "2", "20", "--json"]) == pytest.approx(
        {"vsupply": 5, "vf": 2, "target_ma": 20, "ideal_ohms": 150,
         "ohms": 150, "ma": 20, "power_mw": 60}
    )


def test_rcolor_json_is_utf8_not_escaped(capsys):
    main(["rcolor", "--json", "brown", "black", "red", "gold"])
    assert "kΩ" in capsys.readouterr().out


@pytest.mark.parametrize(
    "argv",
    [
        ["divider", "5", "1000", "1000"],
        ["dbm", "--dbm", "20"],
        ["rcolor", "yellow", "violet", "red", "gold"],
        ["led", "12", "3.2", "10"],
    ],
)
def test_text_output_without_flag_is_not_json(capsys, argv):
    main(argv)
    with pytest.raises(json.JSONDecodeError):
        json.loads(capsys.readouterr().out)


@pytest.mark.parametrize(
    "argv",
    [
        ["divider", "--json", "5", "0", "0"],
        ["dbm", "--json", "--mw", "0"],
        ["rcolor", "--json", "brown", "black", "red", "pink"],
        ["led", "--json", "3", "3.2", "20"],
        ["led", "--json", "5", "2", "0"],
    ],
)
def test_errors_still_exit_2_with_empty_stdout(capsys, argv):
    with pytest.raises(SystemExit) as exc:
        main(argv)
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "error:" in captured.err


def test_non_finite_result_is_an_error_not_invalid_json(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["divider", "--json", "inf", "1", "1"])
    assert exc.value.code == 2
    assert capsys.readouterr().out == ""
