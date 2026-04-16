import requests
import os
from config import BOT_TOKEN


def get_file_path(file_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
    response = requests.get(url).json()

    if not response.get("ok"):
        raise Exception("Failed to get file path")

    return response["result"]["file_path"]


def download_file(file_id, save_path):
    file_path = get_file_path(file_id)

    download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

    response = requests.get(download_url)

    with open(save_path, "wb") as f:
        f.write(response.content)

    return save_path


def download_multiple(file_ids, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    downloaded_files = []

    for i, file_id in enumerate(file_ids, start=1):
        file_name = f"part{i}"
        save_path = os.path.join(output_folder, file_name)

        print(f"Downloading part {i}...")
        download_file(file_id, save_path)

        downloaded_files.append(save_path)

    return downloaded_files