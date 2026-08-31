# ABI3 performance checks

Isolated perf. test for #50398 and #50409.

It tests:
- Python floats and ints to Arrow, also with pandas null handling
- bytes to Arrow
- tuples to structs and MonthDayNano intervals
- NumPy unicode to Arrow
- Arrow maps to pandas
- `pc.add` as a control

Each conversion uses 50,000 values.

- baseline: `35c5ffd12173284406e4a2c86405415444e596d7`
- #50409: `27ae9b50e192640c3c394162295a9155d302ea1a`

This only measures the stable API substitutions already made in #50409,
for example replacing direct CPython access with API calls not an actual ABI3 wheel.

## Running it

Build both wheels against the same Arrow C++ build. Install
each wheel into its own Python 3.12 environment together with
`requirements.txt`.

Run both on the same pinned CPU:

```shell
python bench_limited_api.py \
  --rigorous --affinity=4 -o base.json
python bench_limited_api.py \
  --rigorous --affinity=4 -o pr.json

python -m pyperf compare_to base.json pr.json --table
```

The first runs showed around 6-11% slower conversion for floats, pandas null
handling, structs and NumPy unicode. Bytes was noisy, while intervals, maps and
the C++ control did not show a reliable difference.
