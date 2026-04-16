import os
from zipper import create_zip
from splitter import split_file
from telegram_uploader import upload_multiple
from metadata import add_backup_record


def main():
    folder = input("Enter folder path to backup: ")

    print("\n[1] Creating ZIP...")
    zip_path = create_zip(folder)

    size = os.path.getsize(zip_path)

    print("[2] Splitting if needed...")
    parts = split_file(zip_path)

    print(f"[3] Uploading {len(parts)} part(s)...")
    file_ids = upload_multiple(parts)

    print("[4] Saving metadata...")
    add_backup_record(zip_path, file_ids, size)

    print("\n Backup completed successfully!")


if __name__ == "__main__":
    main()