---
name: csv-data-processor
description: Process CSV files with filtering, aggregation, and summary reports
---

# CSV Data Processor Skill

Process CSV files using Python and pandas. Filter rows, aggregate data, handle missing values, and produce summary reports.

## When to use

- When asked to process, analyze, or transform a CSV file
- When asked to filter, aggregate, or summarize tabular data
- When asked to clean data or handle missing values

## Processing workflow

### Step 1: Load and inspect
```python
import pandas as pd

df = pd.read_csv("input.csv")
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"Missing values:\n{df.isnull().sum()}")
```

Always print the shape and column names first before processing.

### Step 2: Handle missing values
Use this priority order:
1. **Numeric columns**: fill with median (not mean — median is robust to outliers)
2. **Categorical columns**: fill with mode or "Unknown"
3. **Date columns**: forward-fill (ffill)
4. **Drop rows** only if >50% of columns are missing

```python
for col in df.select_dtypes(include='number').columns:
    df[col] = df[col].fillna(df[col].median())

for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "Unknown")
```

### Step 3: Filtering
Always use `.query()` or boolean indexing, never iterate rows:
```python
# Good
filtered = df[df["status"] == "active"]
filtered = df.query("value > 100 and category == 'typeA'")

# Bad - never do this
for i, row in df.iterrows():  # NEVER iterate for filtering
    if row["status"] == "active":
        ...
```

### Step 4: Aggregation
Use `.groupby()` with named aggregations:
```python
summary = df.groupby("category").agg(
    total_value=("value", "sum"),
    avg_value=("value", "mean"),
    count=("id", "count")
).reset_index()
```

Always call `.reset_index()` after groupby to produce a clean DataFrame.

### Step 5: Output
- Save processed data to CSV: `df.to_csv("output.csv", index=False)`
- Always use `index=False` to avoid writing row numbers
- For summary reports, write to both CSV and a readable markdown file

## Output format for summary reports

Always produce a markdown file with:
1. Data overview (rows, columns, missing values found)
2. Processing steps taken
3. Summary statistics table
4. Any warnings (e.g., columns with >20% missing values)

## Important rules

- Always use `index=False` when saving CSV files
- Use median for numeric missing values, not mean
- Never iterate rows with `.iterrows()` for filtering or transformation
- Always inspect data before processing — print shape and columns
- Round floating point numbers to 2 decimal places in output
- Sort output by the primary grouping column
- Use UTF-8 encoding when reading/writing: `pd.read_csv("file.csv", encoding="utf-8")`
