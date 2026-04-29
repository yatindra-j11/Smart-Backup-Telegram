import os
import zipfile
from datetime import datetime
from config import BACKUP_FOLDER


def create_backup_folder():
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)


def create_zip(folder_path):
    create_backup_folder()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"backup_{timestamp}.zip"
    zip_path = os.path.join(BACKUP_FOLDER, zip_name)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if os.path.isfile(folder_path):
            # Handle single file
            zipf.write(folder_path, os.path.basename(folder_path))
        elif os.path.isdir(folder_path):
            # Handle folder (existing logic)
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, folder_path)
                    zipf.write(full_path, arcname)
        else:
            raise ValueError(f"Path does not exist: {folder_path}")

    return zip_path