from typing import (
    Optional,
    Callable,
    Union,
    List,
    Dict,
    Any,
    Protocol,
    runtime_checkable,
)

from pydantic import BaseModel, Field


Config = Any
"""@public"""


class CosmiconfigResult(BaseModel):
    """@public"""

    config: Config
    filepath: str
    is_empty: Optional[bool] = Field(default=None)


LoaderResult = Optional[Config]
"""@public"""


# PORT COMMENT: No async at the moment
@runtime_checkable
class Loader(Protocol):
    """@public"""

    def __call__(self, filepath: str, content: str) -> LoaderResult:
        ...


# PORT COMMENT: No async at the moment
@runtime_checkable
class Transform(Protocol):
    """@public"""

    def __call__(
        self, cosmiconfig_result: Optional[CosmiconfigResult]
    ) -> Optional[CosmiconfigResult]:
        ...


class CommonOptions(BaseModel):
    """@public"""

    # PORT COMMENT: `config_prop` is our custom field, because in pyproject.toml
    #               we need to prefix the package name with `tool.`.
    #               Hence we must support multiple props to search for
    config_prop: Optional[Union[str, List[str]]] = Field(default=None)

    package_prop: Optional[Union[str, List[str]]] = Field(default=None)
    search_places: Optional[List[str]] = Field(default=None)
    ignore_empty_search_places: Optional[bool] = Field(default=None)
    stop_dir: Optional[str] = Field(default=None)
    cache: Optional[bool] = Field(default=None)


# PORT COMMENT: No async at the moment
class Options(CommonOptions):
    """@public"""

    loaders: Optional["Loaders"] = Field(default=None)
    transform: Optional[Transform] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True


# PORT COMMENT: No async at the moment
class InternalOptions(BaseModel):
    """@internal"""

    apply_package_property_path_to_configuration: Optional[bool] = Field(default=None)
    meta_config_file_path: Optional[str] = Field(default=None)

    # PORT COMMENT: The below is equivalent to `Required<Options>`
    # PORT COMMENT 2: `config_prop` is our custom field.
    config_prop: Optional[Union[str, List[str]]] = Field(default=None)
    package_prop: Union[str, List[str]] = Field(default=None)
    search_places: List[str] = Field(default=None)
    ignore_empty_search_places: bool = Field(default=None)
    stop_dir: str = Field(default=None)
    cache: bool = Field(default=None)
    loaders: "Loaders" = Field(default=None)
    transform: Transform = Field(default=None)

    class Config:
        arbitrary_types_allowed = True


# PORT COMMENT: Defined separately from InternalOptions because
#               these values can be nullable.
class InternalOverrideOptions(Options):
    """@internal"""

    apply_package_property_path_to_configuration: Optional[bool] = Field(default=None)
    meta_config_file_path: Optional[str] = Field(default=None)


# PORT COMMENT: No async at the moment
Cache = Dict[str, Optional[CosmiconfigResult]]
"""@internal"""


# PORT COMMENT: No async at the moment
Loaders = Dict[str, Loader]
"""@public"""


class PublicExplorerBase(BaseModel):
    """@public"""

    clear_load_cache: Callable[[], None]
    clear_search_cache: Callable[[], None]
    clear_caches: Callable[[], None]


@runtime_checkable
class PublicExplorerSearchFn(Protocol):
    def __call__(self, search_from: Optional[str]) -> Optional[CosmiconfigResult]:
        ...


@runtime_checkable
class PublicExplorerLoadFn(Protocol):
    def __call__(self, filepath: str) -> Optional[CosmiconfigResult]:
        ...


# PORT COMMENT: No async at the moment
class PublicExplorer(PublicExplorerBase):
    """@public"""

    search: PublicExplorerSearchFn
    load: PublicExplorerLoadFn

    class Config:
        arbitrary_types_allowed = True
