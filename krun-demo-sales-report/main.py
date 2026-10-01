"""Generate a small sales report from a local CSV file."""

import argparse
import json
from pathlib import Path

from reporting.analytics import create_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate sales reports from order CSV data.")
    parser.add_argument("--input", type=Path, default=Path("data/orders.csv"))
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    args = parser.parse_args()

    summary = create_report(args.input, args.output)
    print(json.dumps(summary, indent=2))
    print(f"Report files written to {args.output.resolve()}")


if __name__ == "__main__":
    main()
