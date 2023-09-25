import os
from typing import Optional, Union, List

from pycosmiconfig.utils import imdict
from pycosmiconfig.port.types import Options, InternalOptions
from pycosmiconfig.port.util import remove_none_values_from_object
from pycosmiconfig.port.loaders import load_py, load_json, load_toml, load_yaml
from pycosmiconfig.port.ExplorerSync import ExplorerSync
from pycosmiconfig.port.types import Loaders, Transform


# this needs to be hardcoded, as this is intended for end users,
# who can't supply options at this point
meta_search_places = [
    # PORT COMMENT: use `pyproject` instead of `package.json`
    "pyproject.toml",
    "pyproject.tml",
    ".config.json",
    ".config.yaml",
    ".config.yml",
    ".config.toml",
    ".config.tml",
    ".config.py",
]

# do not allow mutation of default loaders. Make sure it is set inside options
default_loaders = imdict(
    {
        ".py": load_py,
        ".json": load_json,
        ".yaml": load_yaml,
        ".yml": load_yaml,
        ".toml": load_toml,
        ".tml": load_toml,
        "noExt": load_yaml,
    }
)

# PORT COMMENT: No async loaders at the moment


def _identity(x):
    return x


def _get_internal_options(module_name: str, options: Options):
    InternalOptions.update_forward_refs()
    meta_explorer = ExplorerSync(
        InternalOptions(
            package_prop="tool.pycosmiconfig",
            config_prop="pycosmiconfig",
            stop_dir=os.getcwd(),
            search_places=meta_search_places,
            ignore_empty_search_places=False,
            apply_package_property_path_to_configuration=True,
            loaders=default_loaders,
            transform=_identity,
            cache=True,
            meta_config_file_path=None,
        )
    )
    meta_config_result = meta_explorer.search()

    if not meta_config_result:
        return InternalOptions(**options.dict())

    meta_config = meta_config_result.config or {}
    if "loaders" in meta_config:
        raise ValueError("Can not specify loaders in meta config file")

    override_options = InternalOptions(**meta_config)

    if override_options.search_places:
        override_options.search_places = [
            path.replace("{name}", module_name)
            for path in override_options.search_places
        ]

    override_options.meta_config_file_path = meta_config_result.filepath

    merged_options = {**options.dict()}
    merged_options.update(remove_none_values_from_object(override_options.dict()))
    return InternalOptions(**merged_options)


def _normalize_options(module_name: str, options: InternalOptions):
    defaults = InternalOptions(
        package_prop=f"tool.{module_name}",
        config_prop=module_name,
        search_places=[
            # PORT COMMENT: use `pyproject` instead of `package.json`
            "pyproject.toml",
            "pyproject.tml",
            f".{module_name}rc",
            f".{module_name}rc.json",
            f".{module_name}rc.yaml",
            f".{module_name}rc.yml",
            f".{module_name}rc.toml",
            f".{module_name}rc.tml",
            f".{module_name}rc.py",
            f".config/{module_name}rc",
            f".config/{module_name}rc.json",
            f".config/{module_name}rc.yaml",
            f".config/{module_name}rc.yml",
            f".config/{module_name}rc.toml",
            f".config/{module_name}rc.tml",
            f".config/{module_name}rc.py",
            f"{module_name}.config.py",
        ],
        ignore_empty_search_places=True,
        stop_dir=os.path.expanduser("~"),
        cache=True,
        transform=_identity,
        loaders=default_loaders,
        meta_config_file_path=None,
    )

    merged_loaders = defaults.loaders or {}
    merged_loaders.update(options.loaders or {})

    merged_options = {**defaults.dict()}
    merged_options.update(remove_none_values_from_object(options.dict()))
    merged_options.update({"loaders": merged_loaders})

    return InternalOptions(**merged_options)


# PORT COMMENT: No async at the moment
def cosmiconfig(
    module_name: str,
    package_prop: Optional[Union[str, List[str]]] = None,
    search_places: Optional[List[str]] = None,
    ignore_empty_search_places: Optional[bool] = None,
    stop_dir: Optional[str] = None,
    cache: Optional[bool] = None,
    loaders: Optional[Loaders] = None,
    transform: Optional[Transform] = None,
):
    # PORT COMMENT: Handle the difference between prop in pyproject.toml
    #               and elsewhere
    config_prop = package_prop
    package_prop = f'tool.{package_prop}'

    Options.update_forward_refs()
    options = Options(
        package_prop=package_prop,
        config_prop=config_prop,
        search_places=search_places,
        ignore_empty_search_places=ignore_empty_search_places,
        stop_dir=stop_dir,
        cache=cache,
        loaders=loaders,
        transform=transform,
    )

    internal_options = _get_internal_options(module_name, options)
    normalized_options = _normalize_options(module_name, internal_options)
    explorer = ExplorerSync(normalized_options)
    return explorer
