"""Round Zyclotron: 5,000 simulator trials across 1k..5k shots.

This is a local state-vector validation round, not a claim of hardware execution.
Exactly 1,000 trials are run at each shot level. The ZYQL Deutsch-Jozsa gate
must classify a constant oracle as 1 and a balanced oracle as REFUSED.
"""
from __future__ import annotations
import json, os, sys, time
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from zyql_quantum_gate import ZYQLQuantumGate

SHOTS_LEVELS = (1000, 2000, 3000, 4000, 5000)
TRIALS_PER_LEVEL = 1000

def run():
    rows = []
    started = time.time()
    for shots in SHOTS_LEVELS:
        counts = Counter()
        for trial in range(TRIALS_PER_LEVEL):
            # Alternate constant and balanced cases to exercise both paths.
            if trial % 2 == 0:
                oracle = lambda _x: 1
                expected = 1
            else:
                oracle = lambda x: x & 1
                expected = "REFUSED"
            result = ZYQLQuantumGate(3, oracle).run_quantum(
                shots=shots, seed=100000 + shots + trial)
            counts[(expected, result["decision"])] += 1
        correct = sum(v for (expected, got), v in counts.items() if expected == got)
        rows.append({"shots": shots, "trials": TRIALS_PER_LEVEL,
                     "correct": correct, "accuracy": correct / TRIALS_PER_LEVEL,
                     "confusion": {f"{a}->{b}": n for (a, b), n in sorted(counts.items(), key=lambda item: (str(item[0][0]), str(item[0][1])))}})
    return {"experiment": "zyclotron_round_1",
            "backend": "local_state_vector_simulator",
            "hardware_executed": False,
            "total_trials": len(SHOTS_LEVELS) * TRIALS_PER_LEVEL,
            "levels": rows, "elapsed_seconds": round(time.time() - started, 3)}

if __name__ == "__main__":
    result = run()
    out = os.path.join(os.path.dirname(__file__), "zyclotron_round_1.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))
