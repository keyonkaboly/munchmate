import kagglehub
import os

def download_dataset():
    path = kagglehub.dataset_download("niszarkiah/food-delivery")
    print("Dataset downloaded to:", path)
    return path