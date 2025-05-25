import os
from typing import List, Set

def crawl_project(root: str, extensions: Set[str] = {".py"}) -> List[str]:
    """Find all files with specified extensions in directory"""
    files = []
    for subdir, _, filenames in os.walk(root):
        for f in filenames:
            if any(f.endswith(ext) for ext in extensions):
                files.append(os.path.join(subdir, f))
    return files 