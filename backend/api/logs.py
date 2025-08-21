from fastapi import HTTPException, APIRouter
from typing import Dict, List
import os


router = APIRouter()

# paths to log files
# NOTE: These paths are relative to the main.py file location since, this router is included as a module
# DEMO: This should be implemented in a cleaner way, but I've done it this way for simplicity.
LOG_FILES = {
    "log1": "build_log_examples/build_log_example_1.txt",
    "log2": "build_log_examples/build_log_example_2.txt",
    "log3": "build_log_examples/build_log_example_3.txt",
    "log4": "build_log_examples/build_log_example_4.txt",
}

# store line-offset indices for each log file
line_indices: Dict[str, List[int]] = {}

def build_index(path: str) -> List[int]:
    # build byte-offset index for a log file
    offsets = [0]
    offset = 0
    with open(path, "rb") as f:  # read as bytes for exact offsets
        for line in f:
            offset += len(line)
            offsets.append(offset)
    return offsets


# Build indices for each log file
for log_name, log_path in LOG_FILES.items():
    if os.path.exists(log_path):
        line_indices[log_name] = build_index(log_path)

@router.get("/get_log_page", tags=["logs"])
def get_log_page(
    file_id: str,
    offset: int = 0,
    limit: int = 100,
):
    # return `limit` lines starting at line `offset` for given log file.
    if file_id not in LOG_FILES:
        raise HTTPException(404, f"File {file_id} not found")

    path = LOG_FILES[file_id]
    index = line_indices[file_id]

    lines = []
    with open(path, "r") as f:
        if offset < len(index):
            f.seek(index[offset])
        for _ in range(limit):
            line = f.readline()
            if not line:
                break
            lines.append(line.rstrip("\n"))

    return {"file": file_id, "offset": offset, "limit": limit, "lines": lines}