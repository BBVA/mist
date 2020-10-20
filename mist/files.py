import os.path

IGNORE_FILES = (
    ".git",
    "__pycache__",
    ".idea"
)

def skip_dir(root: str) -> bool:
    """Get and absolute directory and determinate if skip then or not based
    on IGNORE FILES constant"""
    current_dir = root.split(os.path.sep)[-1]

    if current_dir in IGNORE_FILES:
        return True
    else:
        return False


__all__ = ("skip_dir", )
