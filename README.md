Sure — here is the **short version you can keep in your README**.

# Data Profiler — Run Guide

## 1. Go to the project folder

```powershell
cd C:\Users\kaush\OneDrive\Documents\data_profiler
```

Make sure you see:

```text
pyproject.toml
src/
README.md
```

---

## 2. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

You should see:

```text
(data_profiler) PS C:\...\data_profiler>
```

---

## 3. Install/sync dependencies

Run:

```powershell
uv sync
```

---

## 4. Verify the project imports

Run:

```powershell
uv run python -c "from example.profiler import DataProfiler; from example.readers import CSVReader; print('Imports OK')"
```

You should get:

```text
Imports OK
```

---

## 5. Start Streamlit

Because `app.py` is inside `src/example`:

```powershell
uv run streamlit run src/example/app.py
```

---

## 6. Use the application

In the Streamlit page:

1. Upload your CSV.
2. Start profiling.
3. View the dataset/column statistics and charts.
4. Download the profiling result as `.json`.

---

## 7. For testing

### Small CSV

Upload your small dataset, e.g. 80 KB.

### Large CSV

Upload a large dataset and make sure **chunk processing** is enabled. The application processes the file in batches instead of loading the entire file into memory.

---

## Quick start

Once everything is installed, normally you only need:

```powershell
cd C:\Users\kaush\OneDrive\Documents\data_profiler
.\.venv\Scripts\Activate.ps1
uv sync
uv run streamlit run src/example/app.py
```

That's it.