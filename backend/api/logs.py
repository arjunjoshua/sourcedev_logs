import math

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

max_results = 100

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


@router.get("/logs")
def get_log_page(file_name: str, limit: int = 100, return_only_lines: bool = False, page_number: int = None,
                 offset: int = 0):
    """Return a page of log lines from a specified log file, with pagination support."""
    if file_name not in LOG_FILES:
        raise HTTPException(404, f"File {file_name} not found")

    if page_number is not None and page_number < 1:
        raise HTTPException(400, "page_number must be >= 1")

    path = LOG_FILES[file_name]
    index = line_indices[file_name]

    if page_number is not None and offset == 0:
        # page number starts from 1 on the frontend, that's why page_number - 1
        offset = (page_number - 1) * limit

    lines = []
    with open(path, "r") as f:
        if offset < len(index):
            f.seek(index[offset])
        for _ in range(limit):
            line = f.readline()
            if not line:
                break
            lines.append(line.rstrip("\n"))

    if return_only_lines:
        return lines

    total_pages = math.ceil(len(index) - 1) // limit if limit > 0 else 1

    return {"offset": offset, "limit": limit, "lines": lines, "total_pages": total_pages}


@router.get("/logs/search")
def search_next(file_name: str, query_str: str, page_number:int, page_size: int = 100):
    """
    Search for a keyword in the log file. Searches from the start of the specified page number.
    """
    if file_name not in LOG_FILES:
        raise HTTPException(404, f"File {file_name} not found")

    path = LOG_FILES[file_name]
    index = line_indices[file_name]
    total_lines = len(index) - 1
    offset = (page_number - 1) * page_size
    if offset >= total_lines:
        raise HTTPException(404, f"Page {page_number} is out of range for {file_name}")

    q = query_str.lower()
    matching_line_indices = []
    found_page_index = None

    with open(path, "r") as f:
        f.seek(index[offset])
        for line_number in range(offset, total_lines):
            line = f.readline()
            if not line:
                break
            if q in line.lower():
                page_index = line_number // page_size
                if found_page_index is None:
                    found_page_index = page_index
                if page_index != found_page_index:
                    break
                matching_line_indices.append(line_number)

    if found_page_index is None:
        raise HTTPException(404, f"No more matches found for '{query_str}' in {file_name}")

    found_page_number = found_page_index + 1
    first_match_page = get_log_page(file_name, limit=page_size, page_number=found_page_number)


    return {
        "file": file_name,
        "keyword": query_str,
        "first_match_page_number": found_page_number,
        "first_match_page": first_match_page,
        "occurrences": matching_line_indices,
    }



@router.get("/logs/list_files")
def list_log_files():
    """ List available log files """
    return {"available_logs": list(LOG_FILES.keys())}
