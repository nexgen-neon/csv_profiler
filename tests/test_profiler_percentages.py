import json
from pathlib import Path

import pytest

from example.profiler.data_profiler import DataProfiler
from example.readers.csv_reader import CSVReader


def test_null_percentage_and_unique_percentage(tmp_path):

    # ============================================================
    # 1. CREATE SAMPLE CSV AUTOMATICALLY
    # ============================================================

    csv_path = tmp_path / "sample.csv"

    csv_content = """id,name,age
1,Alice,20
2,Bob,
3,Alice,30
4,Charlie,
5,Bob,40
"""

    csv_path.write_text(
        csv_content,
        encoding="utf-8",
    )

    # ============================================================
    # 2. PREDETERMINED EXPECTED RESULTS
    # ============================================================

    # AGE:
    #
    # 20
    # NULL
    # 30
    # NULL
    # 40
    #
    # 2 null values / 5 total rows × 100
    #
    expected_age_null_percentage = 40.0

    # NAME:
    #
    # Alice
    # Bob
    # Alice
    # Charlie
    # Bob
    #
    # 3 unique values / 5 non-null values × 100
    #
    expected_name_unique_percentage = 60.0

    # ============================================================
    # 3. RUN CSV PROFILER
    # ============================================================

    reader = CSVReader(
        csv_path,
        chunksize=2,
    )

    profiler = DataProfiler(
        top_n=5,
    )

    for batch in reader.read_batches():

        profiler.process_batch(batch)

    # Generate complete profiler result.
    profiler_result = profiler.generate()

    # ============================================================
    # 4. EXTRACT ONLY THE VALUES REQUIRED BY THIS TEST
    # ============================================================

    actual_age_null_percentage = (
        profiler_result[
            "columns"
        ][
            "age"
        ][
            "null_percentage"
        ]
    )

    actual_name_unique_percentage = (
        profiler_result[
            "columns"
        ][
            "name"
        ][
            "categorical"
        ][
            "unique_percentage"
        ]
    )

    # ============================================================
    # 5. VERIFY THE RESULTS
    # ============================================================

    assert (
        actual_age_null_percentage
        == pytest.approx(
            expected_age_null_percentage
        )
    )

    assert (
        actual_name_unique_percentage
        == pytest.approx(
            expected_name_unique_percentage
        )
    )

    # ============================================================
    # 6. CREATE TEST-ONLY JSON OUTPUT
    # ============================================================

    output_directory = (
        Path(__file__).parent
        / "test_outputs"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    json_path = (
        output_directory
        / "profiling_percentage_test.json"
    )

    # Only store information relevant to THIS test.
    test_result = {

        "test":
            "null_percentage_and_unique_percentage",

        "expected": {

            "age_null_percentage":
                expected_age_null_percentage,

            "name_unique_percentage":
                expected_name_unique_percentage,
        },

        "actual": {

            "age_null_percentage":
                actual_age_null_percentage,

            "name_unique_percentage":
                actual_name_unique_percentage,
        },

        "status":
            "passed",
    }

    with json_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            test_result,
            file,
            indent=4,
        )

    # ============================================================
    # 7. VERIFY JSON WAS CREATED
    # ============================================================

    assert json_path.exists()

    # ============================================================
    # 8. READ THE TEST JSON BACK
    # ============================================================

    with json_path.open(
        "r",
        encoding="utf-8",
    ) as file:

        saved_result = json.load(file)

    # ============================================================
    # 9. VERIFY THE STORED JSON
    # ============================================================

    assert (
        saved_result["expected"]
        ["age_null_percentage"]
        == 40.0
    )

    assert (
        saved_result["expected"]
        ["name_unique_percentage"]
        == 60.0
    )

    assert (
        saved_result["actual"]
        ["age_null_percentage"]
        == pytest.approx(40.0)
    )

    assert (
        saved_result["actual"]
        ["name_unique_percentage"]
        == pytest.approx(60.0)
    )

    assert (
        saved_result["status"]
        == "passed"
    )

    # ============================================================
    # 10. CLEANUP
    # ============================================================

    # sample.csv is inside tmp_path.
    #
    # pytest automatically removes it after the test.
    #
    # The JSON is intentionally kept in:
    #
    # tests/test_outputs/profiling_percentage_test.json
    #
    # so you can inspect the test result.