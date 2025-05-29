import os

def ensure_downloads_folder(path="downloads"):
    os.makedirs(path, exist_ok=True)
