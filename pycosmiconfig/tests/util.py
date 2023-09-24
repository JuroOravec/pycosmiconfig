import os
from pathlib import Path
import shutil
import tempfile
from unittest.mock import Mock
from typing import List


def normalize_directory_slash(pathname: str) -> str:
    return pathname.replace("\\", "/")


class TempDir:
    def __init__(self):
        # Get the actual path for temp directories that are symlinks (MacOS).
        # Without the actual path, tests that use process.chdir will unexpectedly
        # return the real path instead of symlink path.
        temp_dir = os.path.realpath(tempfile.gettempdir())

        # Get the pathname of the file that imported util.py.
        # Used to create a unique directory name for each test suite.
        parent = __file__ or "cosmiconfig"
        relative_parent = Path(parent).relative_to(Path.cwd())

        # Each temp directory will be unique to the test file.
        # This ensures that temp files/dirs won't cause side effects for other tests.
        self.dir = Path(temp_dir, "cosmiconfig", f"{relative_parent}-dir")
        self.dir.mkdir(parents=True, exist_ok=True)

    def absolute_path(self, dir_: str) -> Path:
        # Join paths to ensure dir is always inside the working temp directory
        return self.dir / dir_

    def create_dir(self, dir_: str) -> None:
        dirname = self.absolute_path(dir_)
        dirname.mkdir(parents=True, exist_ok=True)

    def create_file(self, file: str, contents: str) -> None:
        file_path = self.absolute_path(file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(f"{contents}\n")

    def get_spy_path_calls(self, spy: Mock) -> List[str]:
        calls = spy.call_args_list
        result = []
        for call in calls:
            file_path = call.args[0]
            relative_path = Path(file_path).relative_to(self.dir)
            normalize_cross_platform = normalize_directory_slash(str(relative_path))
            result.append(normalize_cross_platform)
        return result

    def clean(self) -> None:
        shutil.rmtree(self.dir, ignore_errors=True)

    def delete_temp_dir(self) -> None:
        shutil.rmtree(self.dir, ignore_errors=True)


def is_not_mjs(file_path: str) -> bool:
    return Path(file_path).suffix != ".mjs"
