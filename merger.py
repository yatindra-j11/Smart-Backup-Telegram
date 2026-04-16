def merge_files(part_files, output_file):
    with open(output_file, "wb") as outfile:
        for part in part_files:
            with open(part, "rb") as infile:
                outfile.write(infile.read())

    return output_file