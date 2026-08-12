import json
import os
import tempfile
import time

import pandas as pd
import streamlit as st

from example.profiler import DataProfiler
from example.readers import CSVReader


st.set_page_config(
    page_title="Data Profiler",
    page_icon="📊",
    layout="wide",
)


st.title("📊 Data Profiler")

st.write(
    "Profile small and large CSV datasets "
    "without loading the entire dataset into memory."
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

with st.sidebar:

    st.header("⚙️ Settings")

    chunk_size = st.number_input(
        "Rows per processing batch",
        min_value=10_000,
        max_value=1_000_000,
        value=100_000,
        step=10_000,
        help=(
            "Controls how many rows are "
            "processed at a time."
        ),
    )

    top_n = st.number_input(
        "Top categorical values",
        min_value=1,
        max_value=20,
        value=5,
        step=1,
    )


# ---------------------------------------------------------
# Input
# ---------------------------------------------------------

st.subheader("📁 Dataset")

input_mode = st.radio(
    "Choose input method",
    [
        "Upload CSV",
        "Use local CSV path",
    ],
    horizontal=True,
)


uploaded_file = None
local_path = None


if input_mode == "Upload CSV":

    uploaded_file = st.file_uploader(
        "Upload your CSV file",
        type=["csv"],
    )

else:

    local_path = st.text_input(
        "Enter the full CSV path",
        placeholder=(
            r"C:\data\large_dataset.csv"
        ),
    )


# ---------------------------------------------------------
# Helper
# ---------------------------------------------------------

def profile_source(
    reader,
):

    profiler = DataProfiler(
        top_n=int(top_n)
    )

    progress_bar = st.progress(
        0
    )

    status = st.empty()

    start_time = time.perf_counter()

    batch_count = 0

    try:

        for batch in reader.read_batches(
            chunksize=int(chunk_size)
        ):

            profiler.process_batch(
                batch
            )

            batch_count += 1

            status.write(
                f"Processed batch "
                f"{batch_count:,} — "
                f"{len(batch):,} rows"
            )

            # We intentionally do not calculate
            # progress from file percentage here.
            # This avoids expensive file-size
            # operations for huge inputs.

            progress_bar.progress(
                min(
                    0.99,
                    batch_count / (
                        batch_count + 10
                    ),
                )
            )

        result = profiler.generate()

        elapsed = (
            time.perf_counter()
            - start_time
        )

        progress_bar.progress(
            1.0
        )

        status.success(
            f"Profiling completed in "
            f"{elapsed:.2f} seconds."
        )

        return result

    except Exception as exc:

        progress_bar.empty()

        status.error(
            f"Profiling failed: {exc}"
        )

        return None


# ---------------------------------------------------------
# Start
# ---------------------------------------------------------

if st.button(
    "🚀 Start Profiling",
    type="primary",
    use_container_width=True,
):

    reader = None

    if input_mode == "Upload CSV":

        if uploaded_file is None:

            st.warning(
                "Please upload a CSV file first."
            )

            st.stop()

        reader = CSVReader(
            uploaded_file,
            chunksize=int(chunk_size),
        )

        file_name = uploaded_file.name

    else:

        if not local_path:

            st.warning(
                "Please enter a CSV path."
            )

            st.stop()

        if not os.path.isfile(
            local_path
        ):

            st.error(
                "The specified file does not exist."
            )

            st.stop()

        reader = CSVReader(
            local_path,
            chunksize=int(chunk_size),
        )

        file_name = os.path.basename(
            local_path
        )

    result = profile_source(
        reader
    )

    if result is not None:

        result[
            "dataset"
        ]["name"] = file_name

        st.session_state[
            "profile_result"
        ] = result


# ---------------------------------------------------------
# Display
# ---------------------------------------------------------

if "profile_result" in st.session_state:

    result = st.session_state[
        "profile_result"
    ]

    dataset = result[
        "dataset"
    ]

    columns = result[
        "columns"
    ]

    st.divider()

    st.header("📈 Profile Results")

    tab_overview, tab_columns, tab_numeric, tab_categorical, tab_json = st.tabs(
        [
            "Overview",
            "Columns",
            "Numerical",
            "Categorical",
            "JSON",
        ]
    )

    # -----------------------------------------------------
    # Overview
    # -----------------------------------------------------

    with tab_overview:

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Rows",
            f"{dataset['rows']:,}",
        )

        c2.metric(
            "Columns",
            f"{dataset['columns']:,}",
        )

        c3.metric(
            "Memory",
            f"{dataset['memory_usage_mb']:.2f} MB",
        )

        c4.metric(
            "Missing %",
            f"{dataset['overall_missing_percentage']:.2f}%",
        )

        st.subheader(
            "Dataset Statistics"
        )

        overview_df = pd.DataFrame(
            {
                "Metric": [
                    "Rows",
                    "Columns",
                    "Memory (MB)",
                    "Missing values",
                    "Missing percentage",
                    "Completely empty rows",
                    "Completely empty columns",
                ],
                "Value": [
                    dataset["rows"],
                    dataset["columns"],
                    round(
                        dataset[
                            "memory_usage_mb"
                        ],
                        2,
                    ),
                    dataset[
                        "missing_values"
                    ],
                    round(
                        dataset[
                            "overall_missing_percentage"
                        ],
                        2,
                    ),
                    dataset[
                        "completely_empty_rows"
                    ],
                    len(
                        dataset[
                            "completely_empty_columns"
                        ]
                    ),
                ],
            }
        )

        st.dataframe(
            overview_df,
            use_container_width=True,
        )

        if dataset[
            "completely_empty_columns"
        ]:

            st.warning(
                "Completely empty columns: "
                + ", ".join(
                    dataset[
                        "completely_empty_columns"
                    ]
                )
            )

    # -----------------------------------------------------
    # Columns
    # -----------------------------------------------------

    with tab_columns:

        search = st.text_input(
            "🔎 Search columns"
        )

        rows = []

        for name, info in columns.items():

            if search.lower() not in (
                name.lower()
            ):
                continue

            rows.append(
                {
                    "Column":
                        name,

                    "Pandas dtype":
                        info[
                            "pandas_dtype"
                        ],

                    "Semantic type":
                        info[
                            "semantic_type"
                        ],

                    "Null count":
                        info[
                            "null_count"
                        ],

                    "Null %":
                        round(
                            info[
                                "null_percentage"
                            ],
                            2,
                        ),
                }
            )

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
        )

    # -----------------------------------------------------
    # Numerical
    # -----------------------------------------------------

    with tab_numeric:

        numerical_rows = []

        for name, info in columns.items():

            if info[
                "semantic_type"
            ] != "numeric":

                continue

            stats = info[
                "statistics"
            ]

            numerical_rows.append(
                {
                    "Column":
                        name,

                    "Min":
                        stats[
                            "minimum"
                        ],

                    "Max":
                        stats[
                            "maximum"
                        ],

                    "Mean":
                        stats[
                            "mean"
                        ],

                    "Median":
                        stats[
                            "median"
                        ],

                    "Std":
                        stats[
                            "standard_deviation"
                        ],

                    "Variance":
                        stats[
                            "variance"
                        ],

                    "IQR":
                        stats[
                            "iqr"
                        ],

                    "Outliers":
                        stats[
                            "outliers"
                        ][
                            "count"
                        ],
                }
            )

        if numerical_rows:

            numeric_df = pd.DataFrame(
                numerical_rows
            )

            st.dataframe(
                numeric_df,
                use_container_width=True,
            )

            st.bar_chart(
                numeric_df.set_index(
                    "Column"
                )[
                    [
                        "Mean",
                        "Median",
                    ]
                ]
            )

        else:

            st.info(
                "No numerical columns found."
            )

    # -----------------------------------------------------
    # Categorical
    # -----------------------------------------------------

    with tab_categorical:

        categorical_rows = []

        for name, info in columns.items():

            if info[
                "semantic_type"
            ] != "categorical":

                continue

            categorical = info[
                "categorical"
            ]

            categorical_rows.append(
                {
                    "Column":
                        name,

                    "Unique values":
                        categorical[
                            "unique_values"
                        ],

                    "Unique %":
                        categorical[
                            "unique_percentage"
                        ],
                }
            )

        if categorical_rows:

            categorical_df = pd.DataFrame(
                categorical_rows
            )

            st.dataframe(
                categorical_df,
                use_container_width=True,
            )

            st.bar_chart(
                categorical_df.set_index(
                    "Column"
                )[
                    "Unique values"
                ]
            )

            st.subheader(
                "Top Values"
            )

            for name, info in columns.items():

                if info[
                    "semantic_type"
                ] != "categorical":

                    continue

                st.write(
                    f"### {name}"
                )

                top_values = info[
                    "categorical"
                ][
                    "most_frequent_values"
                ]

                if top_values:

                    st.dataframe(
                        pd.DataFrame(
                            top_values
                        ),
                        use_container_width=True,
                    )

        else:

            st.info(
                "No categorical columns found."
            )

    # -----------------------------------------------------
    # JSON
    # -----------------------------------------------------

    with tab_json:

        json_string = json.dumps(
            result,
            indent=2,
            default=str,
        )

        st.download_button(
            label="⬇️ Download JSON Profile",
            data=json_string,
            file_name=(
                f"{dataset['name']}"
                ".profile.json"
            ),
            mime="application/json",
            use_container_width=True,
        )

        st.json(result)