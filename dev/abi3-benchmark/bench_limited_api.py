import math

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyperf


N = 50_000

FLOATS = [float(i % 1000) + 0.25 for i in range(N)]
FLOATS_WITH_NULLS = [
    None if i % 101 == 0 else math.nan if i % 97 == 0 else float(i % 1000)
    for i in range(N)
]
INTS_WITH_NULLS = [None if i % 101 == 0 else i for i in range(N)]
BYTES = [(f"value-{i % 1000:04d}").encode() for i in range(N)]

STRUCT_TYPE = pa.struct([("value", pa.float64()), ("label", pa.binary())])
STRUCT_TUPLES = [(float(i), BYTES[i]) for i in range(N)]

INTERVAL_TYPE = pa.month_day_nano_interval()
INTERVALS = [(i % 12, i % 31, i * 1000) for i in range(N)]

NUMPY_UNICODE = np.array(
    [f"value-{i % 1000:04d}" for i in range(N)], dtype="U10"
)

MAP_TYPE = pa.map_(pa.int64(), pa.float64())
MAP_ARRAY = pa.array(
    [[(i, float(i)), (i + 1, float(i + 1))] for i in range(N // 5)],
    type=MAP_TYPE,
)

CONTROL_LEFT = pa.array(np.arange(N, dtype=np.int64))
CONTROL_RIGHT = pa.array(np.arange(N, dtype=np.int64))


def python_float_to_arrow():
    return pa.array(FLOATS, type=pa.float64(), from_pandas=False)


def python_float_to_arrow_from_pandas():
    return pa.array(FLOATS_WITH_NULLS, type=pa.float64(), from_pandas=True)


def python_int_to_arrow_from_pandas():
    return pa.array(INTS_WITH_NULLS, type=pa.int64(), from_pandas=True)


def python_bytes_to_arrow():
    return pa.array(BYTES, type=pa.binary(), from_pandas=False)


def python_tuples_to_struct():
    return pa.array(STRUCT_TUPLES, type=STRUCT_TYPE, from_pandas=False)


def python_tuples_to_interval():
    return pa.array(INTERVALS, type=INTERVAL_TYPE, from_pandas=False)


def numpy_unicode_to_arrow():
    return pa.array(NUMPY_UNICODE)


def arrow_map_to_pandas():
    return MAP_ARRAY.to_pandas()


def cpp_compute_control():
    return pc.add(CONTROL_LEFT, CONTROL_RIGHT)


if __name__ == "__main__":
    runner = pyperf.Runner()
    runner.metadata["pyarrow_version"] = pa.__version__
    runner.metadata["numpy_version"] = np.__version__

    runner.bench_func("python_float_to_arrow", python_float_to_arrow)
    runner.bench_func(
        "python_float_to_arrow_from_pandas",
        python_float_to_arrow_from_pandas,
    )
    runner.bench_func(
        "python_int_to_arrow_from_pandas",
        python_int_to_arrow_from_pandas,
    )
    runner.bench_func("python_bytes_to_arrow", python_bytes_to_arrow)
    runner.bench_func("python_tuples_to_struct", python_tuples_to_struct)
    runner.bench_func("python_tuples_to_interval", python_tuples_to_interval)
    runner.bench_func("numpy_unicode_to_arrow", numpy_unicode_to_arrow)
    runner.bench_func("arrow_map_to_pandas", arrow_map_to_pandas)
    runner.bench_func("cpp_compute_control", cpp_compute_control)
