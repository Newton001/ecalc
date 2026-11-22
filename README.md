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

### `led` — LED series resistor

Supply voltage (V), LED forward voltage (V) and target current (mA). The ideal
resistance `(Vsupply − Vf) / I` is rounded **up** to the nearest E12 value, so
the LED current never exceeds the target; the actual current and the resistor's
power dissipation are then calculated for that E12 value.

```console
$ ecalc led 12 3.2 10
R = 1 kΩ (E12; calculated 880 Ω)
I = 8.8 mA, P = 77.44 mW
```

Pick a resistor rated comfortably above the reported power (e.g. 2× margin).

Invalid input prints an error and exits with status 2.

## Development

```sh
python -m venv .venv
.venv/bin/pip install -e '.[test]'
.venv/bin/pytest
```
