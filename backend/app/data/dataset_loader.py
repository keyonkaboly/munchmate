import kagglehub
import pandas as panda
import os

# Loads raw CSV files
DATASET_NAME = "niszarkiah/food-delivery"

# Function to download the dataset and save it to a path
def download_dataset():
    path = kagglehub.dataset_download(DATASET_NAME)
    print("Downloaded the dataset to path:", path, ".")
    return path

# Function to load csvs, create paths for them
def load_csv(path: str) -> panda.DataFrame:
    # Creates a list of all .csv files inside the path dir.
    csv_files = [f for f in os.listdir(path) if f.endswith(".csv")]
    # Throws error if no csvs
    if not csv_files:
        raise FileNotFoundError("No CSV files found in dir.")
    # Create new paths for csv files w.r.t dir.
    csv_path = os.path.join(path, csv_files[0])
    return panda.read_csv(csv_path)