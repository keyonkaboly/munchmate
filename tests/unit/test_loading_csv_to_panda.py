import pandas as panda
import os
import pytest

from backend.app.data.dataset_loader import load_csv

def test_loading_csv_sucess_scenario(temp_path):
    # Create a test csv file
    test_csv_file = temp_path / "test.csv"
    # Write test text into test csv file
    test_csv_file.write_text("Column 1 | Column 2\n   test  |   test")

