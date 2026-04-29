import requests
from config import BOT_TOKEN, CHAT_ID


def upload_file(file_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"

    with open(file_path, "rb") as f:
        files = {"document": f}
        data = {"chat_id": CHAT_ID}

        response = requests.post(url, files=files, data=data)

    return response.json()


def upload_single(file_path):
    """Upload a single file and return the file_id"""
    res = upload_file(file_path)
    
    if res.get("ok"):
        return res["result"]["document"]["file_id"]
    else:
        raise Exception(f"Upload failed: {res}")


def upload_multiple(files):
    results = []

    for file in files:
        print(f"Uploading {file}...")
        res = upload_file(file)

        if res.get("ok"):
            file_id = res["result"]["document"]["file_id"]
            results.append(file_id)
        else:
            print("Upload failed:", res)

    return results