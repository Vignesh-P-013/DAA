"""DAA Assignment 1: Student registration-number search benchmark.
Run: python3 src/benchmark.py --seed LAST4DIGITS --name "Your Name" --regno "YourRegNo"
Algorithms: iterative linear search, recursive binary search, hash-table lookup.
The third strategy must be changed if your instructor assigned another group-specific algorithm.
"""
import argparse, csv, random, statistics, time, platform, sys
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SIZES = [1_000, 10_000, 100_000, 1_000_000]

class Counter:
    def __init__(self):
        self.comparisons = 0

def linear_search(records, target, counter=None):
    for i, value in enumerate(records):
        if counter is not None:
            counter.comparisons += 1
        if value == target:
            return i
    return -1

def binary_search_recursive(records, target, low=0, high=None, counter=None):
    if high is None:
        high = len(records) - 1
    if low > high:
        return -1
    mid = (low + high) // 2
    if counter is not None:
        counter.comparisons += 1
    if records[mid] == target:
        return mid
    if target < records[mid]:
        return binary_search_recursive(records, target, low, mid - 1, counter)
    return binary_search_recursive(records, target, mid + 1, high, counter)

def build_hash_index(records):
    return {value: i for i, value in enumerate(records)}

def hash_lookup(index, target):
    return index.get(target, -1)

def generate_records(n, seed):
    """Create unique integer registration IDs deterministically from seed."""
    rng = random.Random(seed)
    # Sampling from a large range gives unique IDs without a slow set-building loop.
    records = rng.sample(range(100_000_000, 2_000_000_000), n)
    return records

def median_time_us(fn, repeats=30):
    samples = []
    result = None
    for _ in range(repeats):
        t0 = time.perf_counter()
        result = fn()
        samples.append((time.perf_counter() - t0) * 1_000_000)
    return statistics.median(samples), result

def benchmark_one(n, seed, repeats=30):
    raw = generate_records(n, seed)
    sorted_records = sorted(raw)
    t0 = time.perf_counter()
    index = build_hash_index(raw)
    hash_build_ms = (time.perf_counter() - t0) * 1000
    t0 = time.perf_counter()
    sorted_for_binary = sorted(raw)
    sort_ms = (time.perf_counter() - t0) * 1000
    rng = random.Random(seed + n)
    present = rng.choice(raw)
    absent = 2_100_000_000 + rng.randrange(1_000_000)
    results = []
    for case, target in [("present", present), ("absent", absent)]:
        # Search timings are separate from preprocessing.
        lin_us, lin_result = median_time_us(lambda: linear_search(raw, target), repeats)
        bin_us, bin_result = median_time_us(lambda: binary_search_recursive(sorted_for_binary, target), repeats)
        hash_us, hash_result = median_time_us(lambda: hash_lookup(index, target), repeats)
        expected = raw.index(target) if case == "present" else -1
        assert lin_result == expected
        assert bin_result == (sorted_for_binary.index(target) if case == "present" else -1)
        assert hash_result == expected
        # Comparison counts use one deterministic target, separately from timing.
        lc, bc = Counter(), Counter()
        linear_search(raw, target, lc)
        binary_search_recursive(sorted_for_binary, target, counter=bc)
        results.append({
            "n": n, "case": case, "linear_median_us": round(lin_us, 3),
            "binary_median_us": round(bin_us, 3), "hash_median_us": round(hash_us, 3),
            "linear_comparisons": lc.comparisons, "binary_comparisons": bc.comparisons,
            "hash_build_ms": round(hash_build_ms, 3), "sort_ms": round(sort_ms, 3),
        })
    return results

def run_tests(seed, name, regno):
    cases = [
        ([], 555, -1),
        ([777001], 777001, 0),
        ([777001], 123456, -1),
        ([10, 20, 30, 40, 50], 10, 0),
        ([10, 20, 30, 40, 50], 50, 4),
        ([10, 20, 30, 40, 50], 30, 2),
        ([10, 20, 30, 40, 50], 9, -1),
        ([10, 20, 30, 40, 50], 51, -1),
    ]
    print(f"Name: {name} | Reg No: {regno}")
    print(f"Run timestamp: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    for i, (records, target, expected) in enumerate(cases, 1):
        ordered = sorted(records)
        h = build_hash_index(records)
        assert linear_search(records, target) == expected
        assert binary_search_recursive(ordered, target) == expected
        assert hash_lookup(h, target) == expected
        print(f"TC-{i:02d}: PASS")
    print("All functional tests passed.")

def make_graphs(rows):
    graph_dir = ROOT / "results" / "graphs"
    present = [r for r in rows if r["case"] == "present"]
    absent = [r for r in rows if r["case"] == "absent"]
    for field, title, ylabel, filename in [
        ("linear_median_us", "Median search time by dataset size", "Time (microseconds)", "search_time.png"),
        ("linear_comparisons", "Linear-search comparisons by dataset size", "Comparisons", "linear_comparisons.png"),
        ("binary_comparisons", "Binary-search comparisons by dataset size", "Comparisons", "binary_comparisons.png"),
    ]:
        plt.figure(figsize=(7.5, 4.5))
        for data, label in [(present, "Successful search"), (absent, "Unsuccessful search")]:
            plt.plot([r["n"] for r in data], [r[field] for r in data], marker="o", label=label)
        plt.xscale("log")
        if "time" in filename:
            plt.yscale("log")
        plt.xlabel("Number of records (n)")
        plt.ylabel(ylabel)
        plt.title(title)
        plt.grid(True, which="both", linestyle=":")
        plt.legend()
        plt.tight_layout()
        plt.savefig(graph_dir / filename, dpi=160)
        plt.close()
    plt.figure(figsize=(7.5,4.5))
    plt.plot([r["n"] for r in present], [r["hash_build_ms"] for r in present], marker="o", label="Hash-index build")
    plt.plot([r["n"] for r in present], [r["sort_ms"] for r in present], marker="o", label="Sorting for binary search")
    plt.xscale("log"); plt.yscale("log")
    plt.xlabel("Number of records (n)"); plt.ylabel("Preprocessing time (ms)")
    plt.title("Preprocessing cost"); plt.grid(True, which="both", linestyle=":"); plt.legend()
    plt.tight_layout(); plt.savefig(graph_dir / "preprocessing.png", dpi=160); plt.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=1234, help="Use the last four digits of your registration number")
    parser.add_argument("--name", default="YOUR NAME")
    parser.add_argument("--regno", default="YOUR REGISTRATION NUMBER")
    parser.add_argument("--repeats", type=int, default=30)
    parser.add_argument("--task12-searches", type=int, default=50_000)
    args = parser.parse_args()
    run_tests(args.seed, args.name, args.regno)
    ROOT.joinpath("results").mkdir(exist_ok=True)
    rows = []
    for n in SIZES:
        print(f"\nBenchmarking n={n:,} ...")
        rows.extend(benchmark_one(n, args.seed + n, args.repeats))
    csv_path = ROOT / "results" / "results.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)
    make_graphs(rows)
    # Task 12 benchmark: one million records and 50,000 preselected search queries.
    n = 1_000_000
    raw = generate_records(n, args.seed + n)
    index = build_hash_index(raw)
    rng = random.Random(args.seed + 1212)
    queries = [rng.choice(raw) for _ in range(args.task12_searches)]
    t0 = time.perf_counter()
    found = sum(hash_lookup(index, q) >= 0 for q in queries)
    elapsed = time.perf_counter() - t0
    task12 = {
        "records": n, "queries": args.task12_searches, "found": found,
        "elapsed_seconds": round(elapsed, 6),
        "queries_per_second": round(args.task12_searches / elapsed, 2) if elapsed else None,
        "average_microseconds_per_query": round(elapsed * 1_000_000 / args.task12_searches, 3),
    }
    with (ROOT / "results" / "task12_benchmark.txt").open("w") as f:
        f.write("Task 12 hash-index benchmark\n")
        for k,v in task12.items(): f.write(f"{k}: {v}\n")
    print("\nTask 12 benchmark:")
    for k,v in task12.items(): print(f"{k}: {v}")
    print(f"\nCSV: {csv_path}")
    print(f"Graphs: {ROOT / 'results' / 'graphs'}")
    print("Note: timing results depend on the machine and must be regenerated on your own computer for submission.")

if __name__ == "__main__":
    main()
