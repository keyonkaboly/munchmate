import pandas as panda
import pytest

from app.data.dataset_loader import load_csv

# Note pytest has built in tmp_path that must be used

# Function that proposes a success scenario when loading .csv with checks.
def test_loading_csv_success_scenario(tmp_path):
    ## Setup test part
    # Create a test csv file
    test_csv_file = tmp_path / "test.csv"
    # Write test text into test csv file.
    test_csv_file.write_text("Test Data 1,Test Data 2\ntest,test")
    # Call the function from file
    output = load_csv(str(tmp_path))

    ## Testing part
    # Check if below conditions true if not fail the test
    
    # Check is the test csv file a panda dataframe?
    assert isinstance(output, panda.DataFrame)

    # Check is the .csv empty?
    assert not output.empty

    # Check the Column names, are they what we inputted into the .csv?
    # (Ensure the data is coming correctly)
    assert list(output.columns) == ["Test Data 1", "Test Data 2"]

# Function that checks if empty directory, no csv, run error
def test_loading_csv_error_scenario(tmp_path):
    # Run file not found error
    # If it is run, test passes, if not test fails.
    with pytest.raises(FileNotFoundError):
        load_csv(str(tmp_path))