import json

import pandas as pd
import streamlit as st

from example.readers import CSVReader
from example.profiler import DataProfiler


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Data Profiler",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("📊 Data Profiler")

st.write(
    """
    Upload a CSV file to generate dataset-level
    and column-level profiling.
    """
)


# =========================================================
# FILE UPLOAD
# =========================================================

uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"]
)


# =========================================================
# PROFILE BUTTON
# =========================================================

if uploaded_file is not None:

    st.info(
        f"Selected file: {uploaded_file.name}"
    )

    if st.button(
        "🚀 Start Profiling",
        type="primary"
    ):

        try:

            # -------------------------------------------------
            # INGESTION
            #
            # This is the only CSV-specific part.
            # -------------------------------------------------

            reader = CSVReader(
                uploaded_file
            )

            # -------------------------------------------------
            # READER -> DATAFRAME
            # -------------------------------------------------

            data = reader.read()

            # -------------------------------------------------
            # DATAFRAME -> PROFILER
            # -------------------------------------------------

            profiler = DataProfiler(
                data=data,
                dataset_name=uploaded_file.name
            )

            # -------------------------------------------------
            # GENERATE PROFILE
            # -------------------------------------------------

            profile = profiler.generate()

            # -------------------------------------------------
            # STORE IN SESSION
            # -------------------------------------------------

            st.session_state[
                "data"
            ] = data

            st.session_state[
                "profile"
            ] = profile

            st.session_state[
                "profile_generated"
            ] = True

            st.success(
                "Profiling completed successfully!"
            )

        except Exception as error:

            st.error(
                f"Error while profiling: {error}"
            )


# =========================================================
# DISPLAY PROFILE
# =========================================================

if st.session_state.get(
    "profile_generated",
    False
):

    data = st.session_state[
        "data"
    ]

    profile = st.session_state[
        "profile"
    ]

    dataset = profile[
        "dataset"
    ]

    columns = profile[
        "columns"
    ]


    # =====================================================
    # TABS
    # =====================================================

    (
        overview_tab,
        columns_tab,
        numerical_tab,
        categorical_tab,
        json_tab
    ) = st.tabs(
        [
            "📋 Overview",
            "🧱 Columns",
            "🔢 Numerical",
            "🏷️ Categorical",
            "📄 JSON"
        ]
    )


    # =====================================================
    # OVERVIEW TAB
    # =====================================================

    with overview_tab:

        st.header(
            "Dataset-Level Profiling"
        )

        # -------------------------------------------------
        # FIRST ROW OF METRICS
        # -------------------------------------------------

        col1, col2, col3, col4 = (
            st.columns(4)
        )

        col1.metric(
            "Rows",
            dataset["rows"]
        )

        col2.metric(
            "Columns",
            dataset["columns"]
        )

        col3.metric(
            "Duplicate Rows",
            dataset["duplicate_rows"]
        )

        col4.metric(
            "Missing %",
            f'{dataset["overall_missing_percentage"]}%'
        )


        # -------------------------------------------------
        # SECOND ROW
        # -------------------------------------------------

        col5, col6, col7 = (
            st.columns(3)
        )

        col5.metric(
            "Memory Usage",
            f'{dataset["memory_usage_bytes"]:,} bytes'
        )

        col6.metric(
            "Completely Empty Rows",
            dataset[
                "completely_empty_rows"
            ]
        )

        col7.metric(
            "Completely Empty Columns",
            dataset[
                "completely_empty_columns"
            ]
        )


        # -------------------------------------------------
        # DATA PREVIEW
        # -------------------------------------------------

        st.subheader(
            "Dataset Preview"
        )

        st.dataframe(
            data.head(10),
            use_container_width=True
        )


        # -------------------------------------------------
        # MISSING VALUES
        # -------------------------------------------------

        st.subheader(
            "Missing Values by Column"
        )

        missing_data = pd.DataFrame(
            {
                "Column": list(
                    columns.keys()
                ),

                "Missing %": [
                    columns[column][
                        "null_percentage"
                    ]
                    for column in columns
                ]
            }
        )

        missing_data = (
            missing_data
            .sort_values(
                "Missing %",
                ascending=False
            )
        )

        st.bar_chart(
            missing_data.set_index(
                "Column"
            )
        )


        # -------------------------------------------------
        # SEMANTIC TYPES
        # -------------------------------------------------

        st.subheader(
            "Semantic Data Types"
        )

        semantic_types = pd.Series(
            [
                columns[column][
                    "semantic_type"
                ]
                for column in columns
            ]
        )

        semantic_counts = (
            semantic_types
            .value_counts()
        )

        st.bar_chart(
            semantic_counts
        )


    # =====================================================
    # COLUMNS TAB
    # =====================================================

    with columns_tab:

        st.header(
            "Column-Level Profiling"
        )

        # -------------------------------------------------
        # COLUMN SEARCH
        # -------------------------------------------------

        search = st.text_input(
            "🔍 Search column"
        )

        column_rows = []

        for column_name, info in (
            columns.items()
        ):

            if (
                search
                and
                search.lower()
                not in column_name.lower()
            ):

                continue

            column_rows.append(
                {

                    "Column":
                        column_name,

                    "Pandas dtype":
                        info["dtype"],

                    "Semantic type":
                        info["semantic_type"],

                    "Null count":
                        info["null_count"],

                    "Null %":
                        info["null_percentage"],

                    "Unique count":
                        info["unique_count"],

                    "Unique %":
                        info["unique_percentage"],

                    "Duplicate count":
                        info["duplicate_count"],

                    "Constant":
                        info["constant"],

                    "Near constant":
                        info["near_constant"]
                }
            )

        if column_rows:

            st.dataframe(
                pd.DataFrame(
                    column_rows
                ),
                use_container_width=True
            )

        else:

            st.info(
                "No matching columns found."
            )


        # -------------------------------------------------
        # INDIVIDUAL COLUMN
        # -------------------------------------------------

        st.subheader(
            "Column Details"
        )

        selected_column = st.selectbox(
            "Select a column",
            list(columns.keys())
        )

        selected_info = columns[
            selected_column
        ]

        st.json(
            selected_info
        )


    # =====================================================
    # NUMERICAL TAB
    # =====================================================

    with numerical_tab:

        st.header(
            "Numerical Profiling"
        )

        numerical_columns = [

            column

            for column, info
            in columns.items()

            if info["semantic_type"]
            == "numeric"
        ]

        if not numerical_columns:

            st.info(
                "No numerical columns detected."
            )

        else:

            selected_column = st.selectbox(
                "Select numerical column",
                numerical_columns
            )

            info = columns[
                selected_column
            ]

            statistics = info.get(
                "numeric_statistics",
                {}
            )


            # -------------------------------------------------
            # BASIC STATISTICS
            # -------------------------------------------------

            st.subheader(
                "Basic Statistics"
            )

            col1, col2, col3 = (
                st.columns(3)
            )

            col1.metric(
                "Minimum",
                statistics.get(
                    "min"
                )
            )

            col2.metric(
                "Maximum",
                statistics.get(
                    "max"
                )
            )

            col3.metric(
                "Mean",
                statistics.get(
                    "mean"
                )
            )


            col4, col5, col6 = (
                st.columns(3)
            )

            col4.metric(
                "Median",
                statistics.get(
                    "median"
                )
            )

            col5.metric(
                "Standard Deviation",
                statistics.get(
                    "std"
                )
            )

            col6.metric(
                "Variance",
                statistics.get(
                    "variance"
                )
            )


            # -------------------------------------------------
            # QUARTILES
            # -------------------------------------------------

            st.subheader(
                "Quartiles"
            )

            col1, col2, col3, col4 = (
                st.columns(4)
            )

            col1.metric(
                "Q1",
                statistics.get(
                    "q1"
                )
            )

            col2.metric(
                "Q2",
                statistics.get(
                    "q2"
                )
            )

            col3.metric(
                "Q3",
                statistics.get(
                    "q3"
                )
            )

            col4.metric(
                "IQR",
                statistics.get(
                    "iqr"
                )
            )


            # -------------------------------------------------
            # PERCENTILES
            # -------------------------------------------------

            st.subheader(
                "Percentiles"
            )

            percentile_data = pd.DataFrame(
                [
                    {
                        "Percentile":
                            percentile,

                        "Value":
                            value
                    }

                    for percentile, value
                    in statistics.get(
                        "percentiles",
                        {}
                    ).items()
                ]
            )

            st.dataframe(
                percentile_data,
                use_container_width=True
            )


            # -------------------------------------------------
            # OUTLIERS
            # -------------------------------------------------

            st.subheader(
                "IQR Outliers"
            )

            outliers = statistics.get(
                "outliers",
                {}
            )

            col1, col2, col3 = (
                st.columns(3)
            )

            col1.metric(
                "Outlier Count",
                outliers.get(
                    "count",
                    0
                )
            )

            col2.metric(
                "Outlier %",
                outliers.get(
                    "percentage",
                    0
                )
            )

            col3.metric(
                "Method",
                outliers.get(
                    "method",
                    "IQR"
                )
            )


    # =====================================================
    # CATEGORICAL TAB
    # =====================================================

    with categorical_tab:

        st.header(
            "Categorical Profiling"
        )

        categorical_columns = [

            column

            for column, info
            in columns.items()

            if info["semantic_type"]
            == "categorical"
        ]

        if not categorical_columns:

            st.info(
                "No categorical columns detected."
            )

        else:

            selected_column = st.selectbox(
                "Select categorical column",
                categorical_columns
            )

            info = columns[
                selected_column
            ]

            categorical_statistics = info.get(
                "categorical_statistics",
                {}
            )


            # -------------------------------------------------
            # UNIQUE VALUES
            # -------------------------------------------------

            st.subheader(
                "Unique Values"
            )

            col1, col2 = (
                st.columns(2)
            )

            col1.metric(
                "Unique Values",
                categorical_statistics.get(
                    "unique_values",
                    0
                )
            )

            col2.metric(
                "Unique Percentage",
                f'{categorical_statistics.get(
                    "unique_percentage",
                    0
                )}%'
            )


            # -------------------------------------------------
            # MOST FREQUENT VALUES
            # -------------------------------------------------

            st.subheader(
                "Most Frequent Values"
            )

            most_frequent_values = (
                categorical_statistics.get(
                    "most_frequent_values",
                    []
                )
            )

            if most_frequent_values:

                frequency_data = pd.DataFrame(
                    most_frequent_values
                )

                st.dataframe(
                    frequency_data,
                    use_container_width=True
                )

            else:

                st.info(
                    "No categorical values found."
                )


    # =====================================================
    # JSON TAB
    # =====================================================

    with json_tab:

        st.header(
            "Generated JSON Profile"
        )

        json_profile = json.dumps(
            profile,
            indent=2,
            default=str
        )

        # -------------------------------------------------
        # DOWNLOAD
        # -------------------------------------------------

        st.download_button(
            label="⬇️ Download JSON Profile",

            data=json_profile,

            file_name="profile.json",

            mime="application/json"
        )

        # -------------------------------------------------
        # DISPLAY
        # -------------------------------------------------

        st.code(
            json_profile,
            language="json"
        )