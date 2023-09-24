from pathlib import Path
from typing import Optional, Union

from pycosmiconfig.port.loaders import load_toml
from pycosmiconfig.port.types import CosmiconfigResult, Config
from pycosmiconfig.port.ExplorerBase import ExplorerBase, get_extension_description
from pycosmiconfig.port.util import emplace, get_property_by_path


class ExplorerSync(ExplorerBase):
    """@internal"""

    def load(self, filepath: str) -> CosmiconfigResult:
        filepath = Path(filepath).resolve()

        def load() -> CosmiconfigResult:
            return self._config.transform(self._read_configuration(filepath))

        if self._load_cache:
            return emplace(self._load_cache, str(filepath), load)
        return load()

    def search(self, from_dir_str: str = "") -> Optional[CosmiconfigResult]:
        if self._config.meta_config_file_path:
            self._loading_meta_config = True
            config = self.load(self._config.meta_config_file_path)
            self._loading_meta_config = False
            if config and not config.is_empty:
                return config

        stop_dir = Path(self._config.stop_dir).resolve()
        from_dir = Path(from_dir_str).resolve()

        def _search() -> Optional[CosmiconfigResult]:
            nonlocal from_dir
            if from_dir.is_dir():
                for place in self._config.search_places:
                    filepath = from_dir / place
                    try:
                        result = self._read_configuration(filepath)
                        if result and not (
                            result.is_empty and self._config.ignore_empty_search_places
                        ):
                            return self._config.transform(result)
                    except FileNotFoundError:
                        continue
                    except IsADirectoryError:
                        continue
                    except NotADirectoryError:
                        continue

            parent_dir = from_dir.parent.resolve()
            if from_dir != stop_dir and from_dir != parent_dir:
                from_dir = parent_dir
                if self._search_cache is not None:
                    return emplace(self._search_cache, str(from_dir), _search)
                return _search()
            return self._config.transform(None)

        if self._search_cache is not None:
            return emplace(self._search_cache, str(from_dir), _search)
        return _search()

    def _read_configuration(self, filepath: Union[str, Path]) -> CosmiconfigResult:
        filepath = Path(filepath)
        with open(str(filepath), 'r') as f:
            contents = f.read()
        config = self._load_configuration(filepath, contents)
        return self._to_cosmiconfig_result(str(filepath), config)

    def _load_configuration(self, filepath: Path, contents: str) -> Optional[Config]:
        if not contents.strip():
            return None

        # PORT COMMENT: JS version reads `package.json`
        if filepath.name in ["pyproject.toml", "pyproject.tml"]:
            pyproject_conf = load_toml(str(filepath), contents)
            return get_property_by_path(pyproject_conf, self._config.package_prop)

        extension = filepath.suffix
        try:
            loader = self._config.loaders.get(
                extension or "noExt", self._config.loaders.get("default", None)
            )
            if loader:
                return loader(str(filepath), contents)
        except Exception as error:
            error.filepath = str(filepath)
            raise error
        raise ValueError(
            f"No loader specified for {get_extension_description(extension)}"
        )
