# Sales report demo

This is a standalone Python batch project. It reads a small order CSV, validates
each row, and writes revenue by day and product, a summary, and a list of
rejected rows. It runs on Kaggle CPU without extra Python packages or internet.

After installing KRun and running `krun login`:

```bash
krun demo sales-report
```

The command creates `krun-demo-sales-report/` in your current directory, waits for Kaggle, prints the summary, and downloads the reports to
`.krun/jobs/<job-id>/output/krun_outputs/outputs/`. The bundled data should
produce `total_revenue` of `213.00`, eight paid orders, and two rejected rows.
The result includes `summary.json`, `daily_sales.csv`, `product_sales.csv`, and
`rejected_rows.csv`.

To inspect the job later, use `krun status --project krun-demo-sales-report`
from any writable directory (or replace `status` with `logs` or `output`). These
commands use the most recent job by default.

For a quick local check with Python 3.11+:

```bash
python main.py
```

To try different orders, replace `data/orders.csv` with another CSV containing
`order_id,order_date,product,quantity,unit_price,status`. Valid statuses are
`paid`, `refunded`, and `cancelled`. Amounts are shown with two decimal places.
The remote job receives only the files inside this project directory.
