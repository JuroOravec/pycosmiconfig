from pathlib import Path
from typing import Optional

from pycosmiconfig.port.types import InternalOptions, Cache, Config, CosmiconfigResult
from pycosmiconfig.port.util import get_property_by_path


class ExplorerBase:
    """@internal"""

    def __init__(self, options: InternalOptions) -> None:
        self._loading_meta_config: bool = False
        self._config: InternalOptions = options
        self._load_cache: Optional[Cache] = None
        self._search_cache: Optional[Cache] = None

        if options.cache:
            self._load_cache = {}
            self._search_cache = {}

        self._validate_config()

    def _validate_config(self) -> None:
        for place in self._config.search_places:
            extension = Path(place).suffix
            loader = self._config.loaders.get(extension or "noExt", None)
            if loader is None:
                loader = self._config.loaders.get("default", None)

            if loader is None:
                raise ValueError(
                    f"Missing loader for {get_extension_description(extension)}."
                )
            if not callable(loader):
                desc = get_extension_description(extension)
                loader_type = type(loader).__name__
                raise TypeError(
                    f"Loader for {desc} is not a function: Received {loader_type}."
                )

    def clear_load_cache(self) -> None:
        if self._load_cache:
            self._load_cache.clear()

    def clear_search_cache(self) -> None:
        if self._search_cache:
            self._search_cache.clear()

    def clear_caches(self) -> None:
        self.clear_load_cache()
        self.clear_search_cache()

    def _to_cosmiconfig_result(
        self, filepath: str, config: Config
    ) -> CosmiconfigResult:
        # PORT COMMENT: We don't distinguish between null and undefined
        if config is None:
            return CosmiconfigResult(filepath=filepath, config=None, is_empty=True)

        if (
            self._config.apply_package_property_path_to_configuration
            or self._loading_meta_config
        ):
            prop_name = self._config.config_prop
            if Path(filepath).name in ["pyproject.toml", "pyproject.tml"]:
                prop_name = self._config.package_prop
            config = get_property_by_path(config, prop_name)
        if config is None:
            return CosmiconfigResult(filepath=filepath, config=None, is_empty=True)

        return CosmiconfigResult(config=config, filepath=filepath)


def get_extension_description(extension: Optional[str]) -> str:
    """@internal"""
    return f'extension "{extension}"' if extension else "files without extensions"
