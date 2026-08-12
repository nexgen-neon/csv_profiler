import json

import pandas as pd
import streamlit as st

from example.profiler import DataProfiler
from example.readers import CSVReader


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Data Profiler",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 17px;
        color: #6b7280;
        margin-bottom: 30px;
    }

    .section-title {
        font-size: 27px;
        font-weight: 650;
        margin-top: 30px;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">📊 Data Profiler</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
    Analyze datasets with detailed dataset-level,
    column-level, numerical and categorical profiling.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Profiling Settings")

    top_n = st.slider(
        "Top categorical values",
        min_value=3,
        max_value=20,
        value=5,
    )

    st.divider()

    st.subheader("📦 File Limits")

    st.write(
        "**Maximum upload:** 30 GB"
    )

    st.write(
        "**Processing batch:** 1000 MB"
    )

    st.caption(
        "Large files are processed incrementally "
        "rather than as one complete DataFrame."
    )

    st.divider()

    st.info(
        "Supported format: CSV"
    )


# ============================================================
# FILE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "Upload your dataset",
    type=["csv"],
    max_upload_size=30720,
    help="Maximum file size: 30 GB",
)


# ============================================================
# NO FILE
# ============================================================

if uploaded_file is None:

    st.info(
        "👆 Upload a CSV dataset to begin profiling."
    )

    st.stop()


# ============================================================
# FILE INFORMATION
# ============================================================

file_size_bytes = uploaded_file.size

file_size_mb = (
    file_size_bytes / (1024 * 1024)
)

file_size_gb = (
    file_size_bytes / (1024 * 1024 * 1024)
)


st.success(
    f"Uploaded: **{uploaded_file.name}**"
)


# ============================================================
# FILE SUMMARY
# ============================================================

c1, c2, c3 = st.columns(3)

with c1:

    st.metric(
        "📄 File",
        uploaded_file.name,
    )

with c2:

    if file_size_gb >= 1:

        st.metric(
            "💾 File Size",
            f"{file_size_gb:.2f} GB",
        )

    else:

        st.metric(
            "💾 File Size",
            f"{file_size_mb:.2f} MB",
        )

with c3:

    st.metric(
        "📦 Batch Size",
        "1000 MB",
    )


# ============================================================
# START BUTTON
# ============================================================

start_profiling = st.button(
    "🚀 Start Profiling",
    type="primary",
    use_container_width=True,
)


if start_profiling:

    progress = st.progress(0)

    status = st.empty()

    try:

        # ====================================================
        # CREATE READER
        # ====================================================

        status.info(
            "📥 Initializing dataset reader..."
        )

        uploaded_file.seek(0)

        reader = CSVReader(
            uploaded_file
        )

        # ====================================================
        # CREATE PROFILER
        # ====================================================

        profiler = DataProfiler(
            top_n=top_n
        )

        # ====================================================
        # PROCESS DATA
        # ====================================================

        status.info(
            "🔄 Processing dataset in 1000 MB batches..."
        )

        total_size = uploaded_file.size

        processed_bytes = 0

        batch_number = 0

        for batch in reader.read_batches(
            batch_size_mb=1000
        ):

            batch_number += 1

            status.info(
                f"🔄 Processing batch {batch_number}..."
            )

            profiler.process_batch(
                batch,
                batch_size_bytes=batch.memory_usage(
                    deep=True
                ).sum(),
            )

            processed_bytes += (
                batch.memory_usage(
                    deep=True
                ).sum()
            )

            percentage = min(
                int(
                    (
                        processed_bytes
                        / total_size
                    )
                    * 100
                ),
                99,
            )

            progress.progress(
                percentage
            )

        # ====================================================
        # FINALIZE
        # ====================================================

        status.info(
            "🧮 Finalizing profiling statistics..."
        )

        result = profiler.finalize()

        progress.progress(100)

        status.success(
            "✅ Profiling completed successfully!"
        )

        # ====================================================
        # SAVE RESULT
        # ====================================================

        st.session_state[
            "profile_result"
        ] = result

        st.session_state[
            "profile_filename"
        ] = uploaded_file.name

    except Exception as error:

        progress.empty()

        st.error(
            "❌ Profiling failed."
        )

        st.exception(error)

        st.stop()


# ============================================================
# GET STORED RESULT
# ============================================================

if "profile_result" not in st.session_state:

    st.stop()


result = st.session_state[
    "profile_result"
]


# ============================================================
# DATASET PROFILE
# ============================================================

dataset = result[
    "dataset_profile"
]


st.markdown(
    '<div class="section-title">'
    '📊 Dataset Overview'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# KPI CARDS
# ============================================================

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "Rows",
        f"{dataset['number_of_rows']:,}",
    )

with c2:

    st.metric(
        "Columns",
        f"{dataset['number_of_columns']:,}",
    )

with c3:

    st.metric(
        "Duplicate Rows",
        f"{dataset['duplicate_row_count']:,}",
    )

with c4:

    st.metric(
        "Missing %",
        f"{dataset['overall_missing_percentage']:.2f}%",
    )


# ============================================================
# SECOND KPI ROW
# ============================================================

c1, c2, c3 = st.columns(3)

with c1:

    st.metric(
        "Memory Usage",
        f"{dataset['memory_usage_mb']:.2f} MB",
    )

with c2:

    st.metric(
        "Empty Rows",
        f"{dataset['completely_empty_rows']:,}",
    )

with c3:

    st.metric(
        "Empty Columns",
        f"{len(dataset['completely_empty_columns']):,}",
    )


# ============================================================
# DATASET VISUALIZATION
# ============================================================

st.subheader(
    "📈 Dataset Quality"
)


quality_data = pd.DataFrame(
    {
        "Metric": [
            "Missing %",
            "Duplicate %",
            "Empty Row %",
        ],
        "Percentage": [
            dataset[
                "overall_missing_percentage"
            ],
            (
                dataset[
                    "duplicate_row_count"
                ]
                / max(
                    dataset[
                        "number_of_rows"
                    ],
                    1,
                )
                * 100
            ),
            (
                dataset[
                    "completely_empty_rows"
                ]
                / max(
                    dataset[
                        "number_of_rows"
                    ],
                    1,
                )
                * 100
            ),
        ],
    }
)


st.bar_chart(
    quality_data.set_index(
        "Metric"
    )
)


# ============================================================
# COLUMN PROFILES
# ============================================================

column_profiles = result[
    "column_profiles"
]


st.markdown(
    '<div class="section-title">'
    '🧩 Column Overview'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# COLUMN SUMMARY TABLE
# ============================================================

column_rows = []


for column_name, profile in (
    column_profiles.items()
):

    column_rows.append(
        {
            "Column": column_name,
            "Pandas Type": profile[
                "pandas_dtype"
            ],
            "Semantic Type": profile[
                "semantic_type"
            ],
            "Null Count": profile[
                "null_count"
            ],
            "Null %": profile[
                "null_percentage"
            ],
            "Unique Count": profile[
                "unique_count"
            ],
            "Unique %": profile[
                "unique_percentage"
            ],
        }
    )


column_df = pd.DataFrame(
    column_rows
)


st.dataframe(
    column_df,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# SEMANTIC TYPE DISTRIBUTION
# ============================================================

st.subheader(
    "🧠 Semantic Type Distribution"
)


semantic_counts = (
    column_df[
        "Semantic Type"
    ]
    .value_counts()
)


st.bar_chart(
    semantic_counts
)


# ============================================================
# NULL VALUES BY COLUMN
# ============================================================

st.subheader(
    "🕳️ Missing Values by Column"
)


missing_df = (
    column_df[
        [
            "Column",
            "Null %",
        ]
    ]
    .set_index("Column")
)


st.bar_chart(
    missing_df
)


# ============================================================
# DETAILED COLUMN PROFILES
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🔍 Detailed Column Profiles'
    '</div>',
    unsafe_allow_html=True,
)


for column_name, profile in (
    column_profiles.items()
):

    with st.expander(
        f"📌 {column_name} — "
        f"{profile['semantic_type']}"
    ):

        # ====================================================
        # BASIC INFORMATION
        # ====================================================

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.metric(
                "Data Type",
                profile[
                    "pandas_dtype"
                ],
            )

        with c2:

            st.metric(
                "Semantic Type",
                profile[
                    "semantic_type"
                ],
            )

        with c3:

            st.metric(
                "Null Count",
                profile[
                    "null_count"
                ],
            )

        with c4:

            st.metric(
                "Unique Count",
                profile[
                    "unique_count"
                ],
            )

        # ====================================================
        # NUMERICAL
        # ====================================================

        if (
            profile[
                "semantic_type"
            ]
            == "numeric"
        ):

            numerical = profile[
                "numerical_profile"
            ]

            st.subheader(
                "🔢 Numerical Statistics"
            )

            c1, c2, c3, c4 = st.columns(4)

            with c1:

                st.metric(
                    "Minimum",
                    numerical[
                        "minimum"
                    ],
                )

            with c2:

                st.metric(
                    "Maximum",
                    numerical[
                        "maximum"
                    ],
                )

            with c3:

                st.metric(
                    "Mean",
                    numerical[
                        "mean"
                    ],
                )

            with c4:

                st.metric(
                    "Median",
                    numerical[
                        "median"
                    ],
                )

            c1, c2, c3, c4 = st.columns(4)

            with c1:

                st.metric(
                    "Std. Deviation",
                    numerical[
                        "standard_deviation"
                    ],
                )

            with c2:

                st.metric(
                    "Variance",
                    numerical[
                        "variance"
                    ],
                )

            with c3:

                st.metric(
                    "IQR",
                    numerical[
                        "iqr"
                    ],
                )

            with c4:

                st.metric(
                    "Outliers",
                    numerical[
                        "outlier_count"
                    ],
                )

            # ------------------------------------------------
            # QUANTILES
            # ------------------------------------------------

            st.write(
                "### 📐 Quantiles"
            )

            quantile_data = pd.DataFrame(
                {
                    "Percentile": list(
                        numerical[
                            "quantiles"
                        ].keys()
                    ),
                    "Value": list(
                        numerical[
                            "quantiles"
                        ].values()
                    ),
                }
            )

            st.dataframe(
                quantile_data,
                use_container_width=True,
                hide_index=True,
            )

            # ------------------------------------------------
            # QUANTILE CHART
            # ------------------------------------------------

            st.write(
                "### 📊 Quantile Distribution"
            )

            st.line_chart(
                quantile_data.set_index(
                    "Percentile"
                )
            )

        # ====================================================
        # CATEGORICAL
        # ====================================================

        elif (
            profile[
                "semantic_type"
            ]
            == "categorical"
        ):

            categorical = profile[
                "categorical_profile"
            ]

            st.subheader(
                "🏷️ Categorical Statistics"
            )

            c1, c2 = st.columns(2)

            with c1:

                st.metric(
                    "Unique Values",
                    categorical[
                        "unique_values"
                    ],
                )

            with c2:

                st.metric(
                    "Unique %",
                    f"{categorical['unique_percentage']:.2f}%",
                )

            # ------------------------------------------------
            # TOP VALUES
            # ------------------------------------------------

            top_values = pd.DataFrame(
                categorical[
                    "most_frequent_values"
                ]
            )

            if not top_values.empty:

                st.write(
                    "### 🏆 Most Frequent Values"
                )

                st.dataframe(
                    top_values,
                    use_container_width=True,
                    hide_index=True,
                )

                # --------------------------------------------
                # FREQUENCY CHART
                # --------------------------------------------

                if (
                    "value" in top_values.columns
                    and
                    "frequency"
                    in top_values.columns
                ):

                    chart_data = (
                        top_values[
                            [
                                "value",
                                "frequency",
                            ]
                        ]
                        .set_index("value")
                    )

                    st.bar_chart(
                        chart_data
                    )


# ============================================================
# EXPORT
# ============================================================

st.markdown(
    '<div class="section-title">'
    '📥 Export Report'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# JSON
# ============================================================

json_data = json.dumps(
    result,
    indent=4,
    default=str,
)


download_name = (
    st.session_state[
        "profile_filename"
    ]
    .rsplit(".", 1)[0]
    + "_profile.json"
)


st.download_button(
    label="📥 Download Complete Profile (.JSON)",
    data=json_data,
    file_name=download_name,
    mime="application/json",
    type="primary",
    use_container_width=True,
)


st.caption(
    "The downloaded JSON contains the complete "
    "dataset-level and column-level profiling results."
)