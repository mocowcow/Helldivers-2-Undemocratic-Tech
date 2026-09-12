from pathlib import Path


RESOURCE_ROOT = Path(__file__).resolve().parent


def resource_path(name):
    """Resolve bundled assets from the source or PyInstaller extraction directory."""
    return RESOURCE_ROOT / name
