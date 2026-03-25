import pandas as panda
import pytest

from app.data.dataset_loader import load_csv

""" Function that proposes a success scenario when loading .csv with checks"""
def test_loading_csv_success_scenario(tmp_path):
    test_csv_file = tmp_path / "test.csv"
    test_csv_file.write_text("Test Data 1,Test Data 2\ntest,test")
    output = load_csv(str(tmp_path))

    assert isinstance(output, panda.DataFrame)

    assert not output.empty

    assert list(output.columns) == ["Test Data 1", "Test Data 2"]

"""Function that checks if empty directory, no csv, run error"""
def test_loading_csv_error_scenario(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_csv(str(tmp_path))