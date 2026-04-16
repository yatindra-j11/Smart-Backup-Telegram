import os
from config import MAX_SIZE


def split_file(file_path):
    parts = []

    file_size = os.path.getsize(file_path)

    if file_size <= MAX_SIZE:
        return [file_path]

    part_num = 1

    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(MAX_SIZE)
            if not chunk:
                break

            part_name = f"{file_path}.part{part_num}"

            with open(part_name, "wb") as part_file:
                part_file.write(chunk)

            parts.append(part_name)
            part_num += 1

    return parts