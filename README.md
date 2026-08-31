
# Data Profiler

A Python-based data profiling tool that analyzes datasets and generates detailed dataset-level and column-level profiling information.

The project is designed with an extensible architecture so that data can be loaded from different sources such as CSV files and PostgreSQL databases without changing the profiling logic.

---

## Features

- Dataset-level profiling
  - Number of rows
  - Number of columns
  - Memory usage
  - Completely empty rows
  - Completely empty columns
  - Missing values
  - Overall missing-value percentage

- Column-level profiling
  - Column name
  - Pandas data type
  - Semantic data type
  - Null count and percentage
  - Unique count and percentage
  - Duplicate count
  - Constant / near-constant detection
  - Numerical statistics such as:
    - Minimum
    - Maximum
    - Mean
    - Median
    - Standard deviation

- Categorical profiling
  - Unique values
  - Unique percentage
  - Most frequent values
  - Frequency
  - Frequency percentage

- CSV data source support
- PostgreSQL data source support
- Batch processing for large datasets
- Streamlit web interface
- Automated tests

---

# 1. Prerequisites

Before starting the project, make sure the following are installed on your computer.

## Python

The project requires Python 3.14 or a compatible supported version.

Check your Python installation:

```powershell
python --version
```

You should see something similar to:

```text
Python 3.14.x
```

If Python is not installed, install it from the official Python website:

[Python Downloads](https://www.python.org/downloads/?utm_source=chatgpt.com)

---

## Git

Check whether Git is installed:

```powershell
git --version
```

If Git is not installed, download it from:

[Git](https://git-scm.com/downloads?utm_source=chatgpt.com)

---

## uv

This project uses **uv** for Python environment and dependency management.

Check whether uv is installed:

```powershell
uv --version
```

If uv is not installed, follow the official installation instructions:

[uv Installation Guide](https://docs.astral.sh/uv/getting-started/installation/?utm_source=chatgpt.com)

---

# 2. Clone the Repository

Open PowerShell or a terminal and navigate to the location where you want to keep the project.

For example:

```powershell
cd Documents
```

Clone the repository:

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Move into the project directory:

```powershell
cd data_profiler
```

Verify that you are inside the project:

```powershell
pwd
```

You should see the path to your cloned `data_profiler` directory.

You can also check the project files:

```powershell
dir
```

You should see files/folders similar to:

```text
pyproject.toml
uv.lock
README.md
src
tests
```

---

# 3. Initialize the Python Environment

You do **not** need to manually create a virtual environment using:

```powershell
python -m venv .venv
```

The project uses `uv`.

From the project root directory, run:

```powershell
uv sync
```

`uv sync` will:

1. Create the `.venv` virtual environment if it does not already exist.
2. Read the dependencies from `pyproject.toml`.
3. Use `uv.lock` to install the locked dependency versions.
4. Set up the project environment.

After it finishes, you should have:

```text
data_profiler/
│
├── .venv/
├── src/
├── tests/
├── pyproject.toml
├── uv.lock
└── README.md
```

---

# 4. Activate the Virtual Environment

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, your terminal should look similar to:

```text
(.venv) PS C:\Users\YourName\Documents\data_profiler>
```

The `(.venv)` indicates that the project's virtual environment is active.

---

## PowerShell Execution Policy Issue

If you receive an error such as:

```text
running scripts is disabled on this system
```

you can allow locally created PowerShell scripts for your user account:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate the environment again:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

# 5. Verify the Environment

After activating the environment, check Python:

```powershell
python --version
```

Check uv:

```powershell
uv --version
```

You can also verify that Streamlit is available:

```powershell
streamlit --version
```

If these commands work, the project environment is ready.

---

# 6. Run the Streamlit Application

The main user interface is built using Streamlit.

From the project root directory, run:

```powershell
streamlit run src/example/app.py
```

Alternatively, you can run Streamlit through uv:

```powershell
uv run streamlit run src/example/app.py
```

The terminal should display something similar to:

```text
Local URL: http://localhost:8501
```

Open the displayed URL in your browser.

Usually this is:

```text
http://localhost:8501
```

The Data Profiler interface should now be available.

---

# 7. Using the Streamlit Application

Once the Streamlit application opens:

1. Select the data source.
2. Upload/select the dataset or configure the database connection.
3. Configure profiling options if required.
4. Start the profiling process.
5. Review the generated profiling results.
6. Download the profiling output if the download option is available.

For large datasets, the profiler processes data in batches rather than requiring the entire dataset to be loaded into memory at once.

---

# 8. Running the Tests

Tests are located in the `tests` directory.

First make sure you are in the project root:

```powershell
cd data_profiler
```

Run the test suite with:

```powershell
uv run pytest
```

If you want more detailed output:

```powershell
uv run pytest -v
```

You can also run a specific test file.

For example:

```powershell
uv run pytest tests/test_postgres_reader.py -v
```

---

# 9. PostgreSQL Testing

PostgreSQL support requires a running PostgreSQL server.

If you only want to test the CSV profiler, PostgreSQL is not required.

If you want to test the PostgreSQL reader, install PostgreSQL and create a test database.

The PostgreSQL reader expects a database connection and table from which data can be read.

For example, a test database could contain a table such as:

```text
customers
```

with columns:

```text
id
name
age
city
```

The PostgreSQL reader can then retrieve the data in batches and pass it to the profiler.

---

# 10. Project Structure

The project follows a modular structure similar to:

```text
data_profiler/
│
├── src/
│   └── example/
│       ├── app.py
│       │
│       ├── profiler/
│       │   ├── data_profiler.py
│       │   ├── dataset_profiler.py
│       │   ├── column_profiler.py
│       │   ├── numerical_profiler.py
│       │   └── categorical_profiler.py
│       │
│       └── readers/
│           ├── base_reader.py
│           ├── csv_reader.py
│           └── postgres_reader.py
│
├── tests/
│   ├── test_*.py
│   └── test_postgres_reader.py
│
├── pyproject.toml
├── uv.lock
└── README.md
```

### `readers/`

Responsible for obtaining data.

For example:

```text
CSV → CSVReader
PostgreSQL → PostgreSQLReader
```

The reader layer is separated from the profiling logic so that additional data sources can be added in the future.

### `profiler/`

Contains the actual profiling logic.

The profiler does not need to know whether the data came from a CSV file, PostgreSQL, or another source.

### `data_profiler.py`

Acts as the orchestration layer.

It connects the reader and profiling components together.

### `app.py`

Contains the Streamlit user interface.

### `tests/`

Contains automated tests for the project.

---

# 11. Important: Do Not Modify `uv.lock` Manually

The repository contains:

```text
pyproject.toml
uv.lock
```

`pyproject.toml` defines the project's dependencies.

`uv.lock` contains the locked dependency versions used to reproduce the environment.

When cloning the project, simply run:

```powershell
uv sync
```

Do not manually edit `uv.lock`.

If dependencies are intentionally changed during development, use uv commands such as:

```powershell
uv add pandas
```

or:

```powershell
uv add streamlit
```

Then commit the updated:

```text
pyproject.toml
uv.lock
```

---

# 12. Running Without Activating the Environment

You do not strictly have to activate `.venv`.

Because the project uses uv, you can run commands directly through:

```powershell
uv run
```

For example:

```powershell
uv run pytest
```

and:

```powershell
uv run streamlit run src/example/app.py
```

This is useful because `uv` automatically runs the command inside the project's environment.

Therefore, both workflows are valid.

### Option A — Activate environment

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run src/example/app.py
```

### Option B — Use uv directly

```powershell
uv run streamlit run src/example/app.py
```

For a new user, **Option B is generally the simplest**.

---

# 13. Complete Setup From Scratch

If you are starting from zero, the complete process is:

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

```powershell
cd data_profiler
```

```powershell
uv sync
```

Then start the application:

```powershell
uv run streamlit run src/example/app.py
```

Open:

```text
http://localhost:8501
```

To run the tests:

```powershell
uv run pytest -v
```

That's all that is required for the basic project setup.

---

# 14. Updating an Existing Clone

If the repository has been updated after you cloned it, first pull the latest changes:

```powershell
git pull
```

Then synchronize the environment:

```powershell
uv sync
```

Then run the application again:

```powershell
uv run streamlit run src/example/app.py
```

---

# 15. Troubleshooting

## `uv` is not recognized

If you see:

```text
uv is not recognized as the name of a cmdlet
```

uv is either not installed or is not available in your PATH.

Check:

```powershell
uv --version
```

If it still does not work, install uv using the official installation instructions.

---

## `python` is not recognized

Check whether Python is installed:

```powershell
python --version
```

If it is not available, install Python and restart your terminal.

---

## Streamlit command is not recognized

Instead of:

```powershell
streamlit run src/example/app.py
```

use:

```powershell
uv run streamlit run src/example/app.py
```

This ensures Streamlit is executed from the project's environment.

---

## Import errors

If you see an error such as:

```text
ModuleNotFoundError
```

first try:

```powershell
uv sync
```

Then run the application using:

```powershell
uv run streamlit run src/example/app.py
```

Make sure you are running the command from the project root directory.

---

## Dependency problems

If the environment becomes inconsistent, try:

```powershell
uv sync
```

If the virtual environment itself needs to be recreated, remove `.venv` and run:

```powershell
uv sync
```

On PowerShell:

```powershell
Remove-Item -Recurse -Force .venv
```

Then:

```powershell
uv sync
```

---

# 16. Development Workflow

If you want to modify the project:

```powershell
git pull
```

Make your changes.

Run the tests:

```powershell
uv run pytest -v
```

Run the application:

```powershell
uv run streamlit run src/example/app.py
```

If you add a dependency:

```powershell
uv add <package-name>
```

Then verify everything:

```powershell
uv sync
uv run pytest -v
```

Finally commit your changes:

```powershell
git add .
git commit -m "Describe your changes"
git push
```

---

# 17. Quick Start

If you already have **Git, Python and uv installed**, you only need these commands:

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd data_profiler
uv sync
uv run streamlit run src/example/app.py
```

Then open:

```text
http://localhost:8501
```

To run tests:

```powershell
uv run pytest -v
```

---

# 18. Technology Stack

- Python
- uv
- Pandas
- NumPy
- Streamlit
- SQLAlchemy
- PostgreSQL
- Pytest

---

# 19. Architecture

The project separates **data ingestion** from **data profiling**.

The general flow is:

```text
                 ┌──────────────┐
                 │  Data Source │
                 └──────┬───────┘
                        │
             ┌──────────┴──────────┐
             │                     │
          CSVReader         PostgreSQLReader
             │                     │
             └──────────┬──────────┘
                        │
                        ▼
                ┌───────────────┐
                │ Data Profiler │
                │ Orchestrator  │
                └───────┬───────┘
                        │
             ┌──────────┼──────────┐
             │          │          │
             ▼          ▼          ▼
          Dataset    Column    Categorical/
          Profiler   Profiler   Numerical
                                Profilers
                        │
                        ▼
                 Profiling Result
                        │
                        ▼
                   Streamlit UI
```

This architecture makes it possible to add additional data sources in the future without rewriting the profiling logic.

---

# 20. Support

If you encounter an issue while setting up the project, first check:

```powershell
python --version
uv --version
git --version
```

Then make sure you are in the project root and run:

```powershell
uv sync
uv run pytest -v
```

For application startup:

```powershell
uv run streamlit run src/example/app.py
```