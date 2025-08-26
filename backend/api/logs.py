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
def get_log_page(file_id: str, limit: int = 100, return_only_lines: bool = False, page_number: int = None):
    """Return a page of log lines from a specified log file, with pagination support."""
    if file_id not in LOG_FILES:
        raise HTTPException(404, f"File {file_id} not found")

    if page_number is not None and page_number < 1:
        raise HTTPException(400, "page_number must be >= 1")

    path = LOG_FILES[file_id]
    index = line_indices[file_id]

    if page_number is not None:
        # page number starts from 1 on the frontend, that's why page_number - 1
        offset = (page_number - 1) * limit
    else:
        offset = 0

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

    return {"file": file_id, "offset": offset, "limit": limit, "lines": lines}


@router.get("/logs/search")
def search_logs(file_id: str, keyword: str, page_size: int = 100):
    """
    Initial search — return total matches + the first match page only.
    """
    if file_id not in LOG_FILES:
        raise HTTPException(404, f"File {file_id} not found")

    path = LOG_FILES[file_id]
    total_matches = 0
    first_match_page = None
    first_line = None

    with open(path, "r") as f:
        for line_number, line in enumerate(f):
            if keyword.lower() in line.lower():
                total_matches += 1
                if first_match_page is None:  # capture first match only
                    first_line = line_number
                    first_page_offset = (first_line // page_size) * page_size
                    first_match_page = get_log_page(file_id, offset=first_page_offset, limit=page_size)

    return {
        "file": file_id,
        "keyword": keyword,
        "total_matches": total_matches,
        "first_match_line": first_line,
        "first_match_page": first_match_page,
    }


@router.get("/logs/search_next")
def search_next(file_id: str, keyword: str, match_index: int, page_size: int = 100):
    """
    Get the page for the Nth match (e.g. match_index=0 for first match, 1 for second, etc.)
    """
    if file_id not in LOG_FILES:
        raise HTTPException(404, f"File {file_id} not found")

    path = LOG_FILES[file_id]
    current_index = 0
    target_line = None

    with open(path, "r") as f:
        for line_number, line in enumerate(f):
            if keyword.lower() in line.lower():
                if current_index == match_index:
                    target_line = line_number
                    break
                current_index += 1

    if target_line is None:
        raise HTTPException(404, f"Match index {match_index} not found")

    page_number = (target_line // page_size) + 1
    return {
        "file": file_id,
        "keyword": keyword,
        "match_index": match_index,
        "line_number": target_line,
        "page": get_log_page(file_id, limit=page_size, page_number=page_number),
    }


@router.get("/logs/list_files")
def list_log_files():
    """ List available log files """
    return {"available_logs": list(LOG_FILES.keys())}