"""Validate order rows and aggregate a small sales report."""

import csv
import json
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

REQUIRED_COLUMNS = (
    "order_id",
    "order_date",
    "product",
    "quantity",
    "unit_price",
    "status",
)
VALID_STATUSES = {"paid", "refunded", "cancelled"}
CENT = Decimal("0.01")


def _parse_row(row: dict[str, str | None]) -> tuple[str, str, int, Decimal, str]:
    order_id = (row["order_id"] or "").strip()
    product = (row["product"] or "").strip()
    status = (row["status"] or "").strip().lower()
    if not order_id or not product:
        raise ValueError("order_id and product are required")

    raw_date = (row["order_date"] or "").strip()
    try:
        order_date = date.fromisoformat(raw_date).isoformat()
    except ValueError as exc:
        raise ValueError("order_date must be YYYY-MM-DD") from exc

    try:
        quantity = int(row["quantity"] or "")
        unit_price = Decimal(row["unit_price"] or "")
    except (ValueError, InvalidOperation) as exc:
        raise ValueError("quantity and unit_price must be numeric") from exc
    if quantity <= 0 or not unit_price.is_finite() or unit_price < 0:
        raise ValueError("quantity must be positive and unit_price non-negative")
    if status not in VALID_STATUSES:
        raise ValueError(f"status must be one of {', '.join(sorted(VALID_STATUSES))}")
    return order_date, product, quantity, unit_price, status


def _write_csv(path: Path, columns: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def create_report(input_path: Path, output_dir: Path) -> dict[str, object]:
    """Read a CSV and write daily/product totals plus rejected rows."""
    daily_sales: dict[str, Decimal] = defaultdict(Decimal)
    product_sales: dict[str, Decimal] = defaultdict(Decimal)
    rejected: list[dict[str, str]] = []
    paid_orders = 0
    refunded_orders = 0
    cancelled_orders = 0

    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not set(REQUIRED_COLUMNS).issubset(reader.fieldnames):
            raise ValueError(f"CSV must contain: {', '.join(REQUIRED_COLUMNS)}")
        for line_number, row in enumerate(reader, start=2):
            try:
                order_date, product, quantity, price, status = _parse_row(row)
            except ValueError as exc:
                rejected.append(
                    {
                        "line": str(line_number),
                        "order_id": (row.get("order_id") or "").strip(),
                        "reason": str(exc),
                    }
                )
                continue
            if status == "paid":
                amount = (price * quantity).quantize(CENT)
                daily_sales[order_date] += amount
                product_sales[product] += amount
                paid_orders += 1
            elif status == "refunded":
                refunded_orders += 1
            else:
                cancelled_orders += 1

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(
        output_dir / "daily_sales.csv",
        ("date", "revenue"),
        [
            {"date": day, "revenue": f"{amount:.2f}"}
            for day, amount in sorted(daily_sales.items())
        ],
    )
    _write_csv(
        output_dir / "product_sales.csv",
        ("product", "revenue"),
        [
            {"product": product, "revenue": f"{amount:.2f}"}
            for product, amount in sorted(product_sales.items())
        ],
    )
    _write_csv(output_dir / "rejected_rows.csv", ("line", "order_id", "reason"), rejected)

    summary: dict[str, object] = {
        "paid_orders": paid_orders,
        "refunded_orders": refunded_orders,
        "cancelled_orders": cancelled_orders,
        "rejected_rows": len(rejected),
        "total_revenue": f"{sum(daily_sales.values(), Decimal('0')):.2f}",
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    return summary
