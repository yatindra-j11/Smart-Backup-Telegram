import os
import zipfile
from metadata import load_metadata
from telegram_downloader import download_multiple
from merger import merge_files


def extract_zip(zip_path, extract_to="restored_files"):
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    return extract_to


def choose_backup(data):
    print("\nAvailable Backups:\n")

    for record in data:
        print(f"{record['backup_id']} - {record['file_name']} ({record['backup_date']})")

    choice = int(input("\nEnter backup ID to restore: "))

    for record in data:
        if record["backup_id"] == choice:
            return record

    return None


def main():
    data = load_metadata()

    if not data:
        print("No backups found.")
        return

    record = choose_backup(data)

    if not record:
        print("Invalid selection.")
        return

    print("\n[1] Downloading parts...")
    parts = download_multiple(record["file_ids"], "temp_parts")

    print("[2] Merging parts...")
    zip_path = merge_files(parts, "restored_backup.zip")

    print("[3] Extracting ZIP...")
    extract_zip(zip_path)

    print("\n Restore completed successfully!")


if __name__ == "__main__":
    main()