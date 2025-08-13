import os
from config.settings import SUPPORTED_FORMATS

def list_mp3_files(folder_path):
    files = []
    for ext in SUPPORTED_FORMATS:
        files.extend([os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(ext.replace("*", ""))])
    return files
