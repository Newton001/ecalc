"""Command-line interface for ecalc."""

import argparse
import json
import sys

from ecalc import __version__, calc


def _cmd_divider(args):
    vout = calc.divider(args.vin, args.r1, args.r2)
    if args.json:
        return {"vin": args.vin, "r1": args.r1, "r2": args.r2, "vout": vout}
    return f"Vout = {vout:.6g} V"


def _cmd_dbm(args):
    if args.dbm is not None:
        dbm, mw = args.dbm, calc.dbm_to_mw(args.dbm)
        text = f"{dbm:g} dBm = {mw:.6g} mW"
    else:
        mw, dbm = args.mw, calc.mw_to_dbm(args.mw)
        text = f"{mw:g} mW = {dbm:.6g} dBm"
    if args.json:
        return {"dbm": dbm, "mw": mw}
    return text


def _cmd_rcolor(args):
    ohms, tol = calc.rcolor(args.bands)
    formatted = f"{calc.format_ohms(ohms)} ±{tol:g}%"
    if args.json:
        return {
            "bands": [calc.normalize_colour(b) for b in args.bands],
            "ohms": ohms,
            "tolerance_percent": tol,
            "formatted": formatted,
        }
    return formatted


def _cmd_led(args):
    ideal, r, ma, watts = calc.led(args.vsupply, args.vf, args.ma)
    print(f"R = {calc.format_ohms(r)} (E12; calculated {calc.format_ohms(round(ideal, 3))})")
    print(f"I = {ma:.4g} mA, P = {watts * 1000:.4g} mW")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="ecalc", description="Tiny electronics calculator."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true",
                        help="print the result as a JSON object")

    p = sub.add_parser("divider", parents=[common],
                       help="voltage divider: Vin, R1, R2 -> Vout")
    p.add_argument("vin", type=float, help="input voltage (V)")
    p.add_argument("r1", type=float, help="top resistor, Vin to Vout (Ω)")
    p.add_argument("r2", type=float, help="bottom resistor, Vout to ground (Ω)")
    p.set_defaults(func=_cmd_divider)

    p = sub.add_parser("dbm", parents=[common], help="convert dBm <-> mW")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--dbm", type=float, metavar="DBM", help="convert dBm to mW")
    g.add_argument("--mw", type=float, metavar="MW", help="convert mW to dBm")
    p.set_defaults(func=_cmd_dbm)

    p = sub.add_parser("rcolor", parents=[common],
                       help="4-band resistor colour code -> ohms ± tolerance")
    p.add_argument("bands", nargs=4, metavar="BAND",
                   help="band colours: digit digit multiplier tolerance")
    p.set_defaults(func=_cmd_rcolor)

    p = sub.add_parser("led", help="LED series resistor: Vsupply, Vf, mA -> E12 resistor + power")
    p.add_argument("vsupply", type=float, help="supply voltage (V)")
    p.add_argument("vf", type=float, help="LED forward voltage (V)")
    p.add_argument("ma", type=float, help="target LED current (mA)")
    p.set_defaults(func=_cmd_led)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
        if args.json:
            # allow_nan=False: NaN/Infinity aren't valid JSON, so fail loudly.
            result = json.dumps(result, allow_nan=False, ensure_ascii=False)
    except ValueError as exc:
        parser.exit(2, f"ecalc {args.command}: error: {exc}\n")
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
