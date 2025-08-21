file_path = "../build_log_examples/build_log_example_1.txt"


def read_log_file(file_path: str = file_path) -> str:
    with open(file_path, "r") as file:
        for line in file:
            yield line


if __name__ == "__main__":
    for line in read_log_file():
        print(line.strip())