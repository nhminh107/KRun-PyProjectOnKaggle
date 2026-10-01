# macOS CPU demo validation
A manual end-to-end run of the native CLI completed on 2026-09-29.
This records one tested configuration, not a guarantee for every macOS version
or every KRun feature.
## Tested environment
- macOS 26.6.2 (25G83), Apple Silicon (arm64).
- Python 3.12.14 in a uv-created virtual environment.
- KRun 0.2.1, local checkout at commit `ca86205c49eff3a6943bebf04b91858e7a6df95e`.
- Editable installation with `uv pip install -e '.[dev]'`.
- Native `krun` command; Docker was not used.
- The checkout path contained spaces and Vietnamese characters.
- Remote workload: CPU, Internet disabled, no additional dependencies declared.
The recorded result applies to the tested commit above, not automatically to
later changes on `main`.
## Reproduce
From a local checkout with the virtual environment activated:
```bash
krun --version
krun --help
krun demo sales-report --copy-only
krun run main.py --project ./krun-demo-sales-report --dry-run
krun login
krun doctor
krun run main.py --project ./krun-demo-sales-report
```
Use a fresh demo destination, or skip the copy step if that directory already
contains the unmodified demo. Dry-run does not authenticate or submit a job;
the final command submits a real job using the authenticated Kaggle account.
## Observed result
The dry-run selected `main.py` and listed 8 files totaling 7,050 bytes.
Authentication and `doctor` passed. The submitted job progressed through
`QUEUED`, `RUNNING`, and `COMPLETE`, then printed `Completed successfully.`
after downloading artifacts.
The downloaded `summary.json` contained:
```json
{
  "paid_orders": 8,
  "refunded_orders": 1,
  "cancelled_orders": 1,
  "rejected_rows": 2,
  "total_revenue": "213.00"
}
```
All four reports were present under
`krun-demo-sales-report/.krun/jobs/<job-id>/output/krun_outputs/outputs/`:
- `summary.json`
- `daily_sales.csv`
- `product_sales.csv`
- `rejected_rows.csv`
Remote `mistune` and `nbconvert` emitted invalid-escape `SyntaxWarning` messages
during HTML conversion. These did not prevent this job from completing or
its artifacts from being downloaded.
## Scope and local test caveat
This validates native CLI startup, demo packaging, Kaggle authentication, CPU
submission, monitoring, and artifact download on this host. It does not certify
GPU/TPU workloads, notebook entrypoints, the Docker launcher, other macOS
versions, or the full automated test suite.
During local test setup, five launcher tests failed when the Python executable
path contained spaces. The test helper writes that path directly into the
fake Docker executable's shebang, which fails to launch and produces a
misleading Docker-not-running message. An environment located at a path without
spaces was used for the successful native CLI demo. This document does not
claim that the launcher test defect has been fixed.
Generated demo directories, `.krun` job state, downloaded artifacts, and Kaggle
credentials are not part of this contribution.
