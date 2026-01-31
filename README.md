# Thoughtful Automation — Package Sorting Function

## Overview

A robotic arm dispatch function that classifies packages into three stacks based on physical dimensions and mass. Designed for clarity, correctness at boundaries, and defensive input handling.

## Quick Start

```bash
python -m pytest test_sort.py -v
```

All 41 tests pass. No external dependencies beyond `pytest`.

## Solution Design

### Classification Logic

Two independent boolean checks drive all routing:

| Flag | Condition |
|---|---|
| **Bulky** | Volume ≥ 1,000,000 cm³ **OR** any single dimension ≥ 150 cm |
| **Heavy** | Mass ≥ 20 kg |

### Dispatch Truth Table

| Bulky | Heavy | Stack |
|---|---|---|
| ✗ | ✗ | STANDARD |
| ✓ | ✗ | SPECIAL |
| ✗ | ✓ | SPECIAL |
| ✓ | ✓ | REJECTED |

This maps cleanly to a short-circuit evaluation: check for REJECTED first (both flags), then SPECIAL (either flag), then default to STANDARD.

### Why This Structure

The two flags are computed independently before any routing decision. This keeps the classification logic and the dispatch logic completely separate — easy to extend either side without touching the other. For example, adding a new flag (e.g., "fragile") would require zero changes to the bulky/heavy logic.

## Test Strategy

Tests are organized into 7 focused groups:

1. **Core Routing** — One clean case per stack to establish the baseline.
2. **Bulky by Volume** — Threshold boundary: exactly at, just above, just below 1,000,000 cm³.
3. **Bulky by Dimension** — Each of the three dimensions tested at exactly 150, just under, and above. Confirms bulky triggers even when volume is tiny.
4. **Heavy Threshold** — Mass at exactly 20, just under, and well above.
5. **Boundary Matrix** — All four corners of the bulky × heavy space at exact threshold values. Includes the tricky case where bulky is triggered by dimension (not volume) combined with heavy → REJECTED.
6. **Edge Cases** — Zero dimensions, very large values, float precision at the volume threshold, and mixed int/float inputs.
7. **Error Handling** — Negative values raise `ValueError`; non-numeric types raise `TypeError`. Each parameter is tested independently.

## Design Decisions

- **Input validation before logic.** A robotic arm receiving garbage data should fail loudly, not silently misroute a package.
- **Type hints on the function signature.** Documents expected units (cm, kg) without requiring a separate spec.
- **No external dependencies.** The sort function is a pure function with zero imports. Maximizes portability for any deployment environment.
- **Float-safe thresholds.** All comparisons use `>=` as specified. Tests deliberately probe float precision boundaries (e.g., `125.0 * 100.0 * 80.0 = 1,000,000` exactly) to confirm correct behavior.
