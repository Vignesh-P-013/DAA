# DAA Assignment 1 — Student Record Search

## Algorithms
1. Iterative linear search.
2. Recursive binary search.
3. Hash-table lookup (Python `dict`).

**Important:** Your faculty's submission rules assign the third strategy by group. Confirm whether your group is permitted to use hash-table lookup. If your group is assigned interpolation, jump/exponential search, or B-tree/BST, replace the third algorithm before submission.

## Requirements
- Python 3.10+
- matplotlib (`python3 -m pip install matplotlib`)

## Run
From the project root:

```bash
python3 src/benchmark.py --seed LAST4DIGITS --name "Your Name" --regno "YourRegNo"
```

Replace `LAST4DIGITS`, `Your Name`, and `YourRegNo` with your details. Use the last four registration-number digits as the seed as required by the assignment rules.

The program runs correctness tests, benchmarks four dataset sizes, writes `results/results.csv`, creates graphs under `results/graphs/`, and runs a 50,000-query hash-index benchmark on one million records.

## Evidence and integrity
- Re-run the benchmark on your own computer.
- Capture genuine screenshots showing your name/registration number, full terminal output, and system date/time.
- Ensure the report's values match your own `results.csv` and screenshots.
- Do not submit example results as if they were measured on your own machine.
- Add at least five meaningful Git commits across the project work; do not fabricate commit history.

## Repository layout
- `src/benchmark.py`: algorithms, tests, benchmark and graphs.
- `results/`: CSV and Task 12 benchmark output.
- `results/graphs/`: generated graphs.
- `report/`: put final report PDF here.
- `screenshots/`: put your genuine screenshots here.
