import sys
import os


def resource_path(relative_path: str) -> str:
    """
    Return the absolute path to a resource, compatible with PyInstaller and development.

    In a PyInstaller one‑file or one‑dir bundle, sys._MEIPASS points to the temporary
    extraction folder. In normal Python execution, the project root is the current
    working directory (or the directory containing main.py).

    Args:
        relative_path: A path relative to the project root (e.g., 'resources/images/logo.png').

    Returns:
        Absolute path to the resource.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running as a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in a normal Python environment
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)