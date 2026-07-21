import os
import csv


def test_summary_csv_exists():
    assert os.path.exists("/workspace/summary.csv")


def test_report_exists():
    assert os.path.exists("/workspace/report.md")


def test_summary_has_correct_columns():
    with open("/workspace/summary.csv") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        assert "department" in headers
