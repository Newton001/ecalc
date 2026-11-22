"""Pure calculation functions used by the CLI."""

import math

DIGITS = {
    "black": 0, "brown": 1, "red": 2, "orange": 3, "yellow": 4,
    "green": 5, "blue": 6, "violet": 7, "grey": 8, "white": 9,
}

MULTIPLIERS = {name: 10 ** d for name, d in DIGITS.items()}
MULTIPLIERS.update({"gold": 0.1, "silver": 0.01})

TOLERANCES = {
    "brown": 1.0, "red": 2.0, "green": 0.5, "blue": 0.25,
    "violet": 0.1, "grey": 0.05, "gold": 5.0, "silver": 10.0,
}

ALIASES = {"gray": "grey", "purple": "violet"}


def divider(vin, r1, r2):
    """Unloaded voltage divider: Vout = Vin * R2 / (R1 + R2)."""
    if r1 < 0 or r2 < 0:
        raise ValueError("resistances must be non-negative")
    if r1 + r2 == 0:
        raise ValueError("R1 + R2 must be greater than zero")
    return vin * r2 / (r1 + r2)


def dbm_to_mw(dbm):
    return 10 ** (dbm / 10)


def mw_to_dbm(mw):
    if mw <= 0:
        raise ValueError("power in mW must be greater than zero")
    return 10 * math.log10(mw)


def _norm(colour):
    c = colour.strip().lower()
    return ALIASES.get(c, c)


def rcolor(bands):
    """Decode a 4-band resistor colour code.

    Returns (resistance_ohms, tolerance_percent).
    """
    if len(bands) != 4:
        raise ValueError("expected exactly 4 colour bands")
    b1, b2, mult, tol = (_norm(b) for b in bands)
    for name, table, band in (
        ("first digit", DIGITS, b1),
        ("second digit", DIGITS, b2),
        ("multiplier", MULTIPLIERS, mult),
        ("tolerance", TOLERANCES, tol),
    ):
        if band not in table:
            raise ValueError(
                f"invalid {name} colour {band!r}; choose from: {', '.join(table)}"
            )
    value = (DIGITS[b1] * 10 + DIGITS[b2]) * MULTIPLIERS[mult]
    return round(value, 2), TOLERANCES[tol]


def format_ohms(ohms):
    """Format a resistance with an SI prefix, e.g. 4700 -> '4.7 kΩ'."""
    for factor, prefix in ((1e9, "G"), (1e6, "M"), (1e3, "k")):
        if ohms >= factor:
            return f"{ohms / factor:g} {prefix}Ω"
    return f"{ohms:g} Ω"


E12 = (1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2)


def e12_ceil(ohms):
    """Smallest E12 preferred value that is >= ohms."""
    if not math.isfinite(ohms) or ohms <= 0:
        raise ValueError("resistance must be a positive finite number")
    exp = math.floor(math.log10(ohms))
    mantissa = ohms / 10 ** exp
    for v in E12 + (10.0,):
        # small tolerance so exact E12 values aren't bumped up by float error
        if v >= mantissa * (1 - 1e-9):
            return float(f"{v * 10 ** exp:.2g}")
    raise AssertionError("unreachable")  # pragma: no cover


def led(vsupply, vf, current_ma):
    """Series resistor for an LED.

    Returns (calculated_ohms, e12_ohms, actual_current_ma, power_w), where the
    E12 value is rounded up (so the LED current never exceeds the target) and
    the actual current and resistor power use that E12 value.
    """
    for name, value in (("supply voltage", vsupply),
                        ("LED forward voltage", vf),
                        ("current", current_ma)):
        if not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number")
    if vf <= 0:
        raise ValueError("LED forward voltage must be greater than zero")
    if current_ma <= 0:
        raise ValueError("current must be greater than zero")
    if vsupply <= vf:
        raise ValueError(
            "supply voltage must be greater than the LED forward voltage"
        )
    vdrop = vsupply - vf
    ideal = vdrop / (current_ma / 1000)
    r = e12_ceil(ideal)
    current_a = vdrop / r
    return ideal, r, current_a * 1000, vdrop * current_a
