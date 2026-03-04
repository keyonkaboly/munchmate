import kagglehub
import pandas as panda
import os

# Loads raw CSV files
DATASET_NAME = "niszarkiah/food-delivery"

# Function to download the dataset and save it to a path
def download_dataset():
    dataset_path = kagglehub.dataset_download(DATASET_NAME)
    print("Downloaded the dataset to path:", dataset_path, ".")
    return dataset_path

# Function to load csvs, create paths for them
def load_csv(dataset_path: str) -> panda.DataFrame:
    # Creates a list of all .csv files inside the path dir.
    csv_files = []

    for file in os.listdir(dataset_path):
        if file.endswith(".csv"):
            csv_files.append(file)

    # Throws error if no csvs
    if not csv_files:
        raise FileNotFoundError("No CSV files found in dir.")
    
    # Create new paths for csv files w.r.t dir.
    csv_path = os.path.join(dataset_path, csv_files[0])
    # Note: read_csv uses commas to separate data
    return panda.read_csv(csv_path)