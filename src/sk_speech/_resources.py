"""Access files shipped inside the installed package."""

from contextlib import contextmanager
from importlib.resources import as_file, files
from pathlib import Path
from typing import Iterator


@contextmanager
def data_path(relative_path: str) -> Iterator[Path]:
    """Yield a real filesystem path for a bundled data file."""

    resource = files("sk_speech").joinpath("data", relative_path)
    with as_file(resource) as path:
        yield path

