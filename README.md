# ecalc — tiny electronics calculator CLI

A small command-line calculator for everyday electronics sums. Pure Python,
standard library only (Python 3.8+).

## Install

From a clone of this repository:

```sh
pip install .            # or: pipx install .
```

This installs an `ecalc` command. You can also run it without installing:

```sh
python -m ecalc --help
```

## Usage

### `divider` — voltage divider

Unloaded divider output, `Vout = Vin × R2 / (R1 + R2)`, where R1 is the top
resistor (Vin → Vout) and R2 the bottom one (Vout → ground). Resistances in ohms.

```console
$ ecalc divider 12 10000 4700
Vout = 3.83673 V
```

### `dbm` — dBm ↔ mW

```console
$ ecalc dbm --dbm 20
20 dBm = 100 mW
$ ecalc dbm --mw 0.5
0.5 mW = -3.0103 dBm
```

### `rcolor` — 4-band resistor colour code

Bands in order: first digit, second digit, multiplier, tolerance. Colour names
are case-insensitive; `gray` and `purple` are accepted for grey and violet.

```console
$ ecalc rcolor yellow violet red gold
4.7 kΩ ±5%
$ ecalc rcolor green blue gold red
5.6 Ω ±2%
```

### Machine-readable output: `--json`

Every subcommand accepts `--json` to print a single JSON object instead of
the human-readable line:

```console
$ ecalc divider --json 12 10000 4700
{"vin": 12.0, "r1": 10000.0, "r2": 4700.0, "vout": 3.836734693877551}
$ ecalc dbm --json --dbm 20
{"dbm": 20.0, "mw": 100.0}
$ ecalc rcolor --json yellow violet red gold
{"bands": ["yellow", "violet", "red", "gold"], "ohms": 4700, "tolerance_percent": 5.0, "formatted": "4.7 kΩ ±5%"}
```

Values are full-precision numbers (not rounded as in text output); `ohms` is
in Ω and `tolerance_percent` in %. `rcolor` reports band names normalised
(lower-case, aliases resolved).

Invalid input prints an error to stderr and exits with status 2, with or
without `--json` (nothing is written to stdout).

## Development

```sh
python -m venv .venv
.venv/bin/pip install -e '.[test]'
.venv/bin/pytest
```
