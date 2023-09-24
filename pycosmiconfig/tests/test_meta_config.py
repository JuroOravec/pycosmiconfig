import builtins
import os
import pytest
from unittest.mock import patch

from pycosmiconfig import cosmiconfig, Options, CosmiconfigResult
from util import TempDir


@pytest.fixture(autouse=True)
def temp():
    temp_dir = TempDir()
    yield temp_dir
    temp_dir.delete_temp_dir()


def test_throws_when_supplied_loaders(temp: TempDir):
    temp.create_file(".config.yml", "pycosmiconfig:\n  loaders: []")

    current_dir = os.getcwd()
    os.chdir(temp.dir)

    with pytest.raises(ValueError):
        cosmiconfig("foo")

    os.chdir(current_dir)


def describe_uses_user_configured_search_places_without_placeholders():
    @pytest.fixture(autouse=True)
    def current_dir(temp: TempDir):
        temp.create_dir("sub")
        temp.create_file(".foorc", "a: b")
        temp.create_file(".foo-config", "a: c")

        current_dir = os.getcwd()
        os.chdir(temp.dir)
        yield current_dir
        os.chdir(current_dir)

    def _run_test(temp: TempDir):
        file = temp.absolute_path(".foo-config")
        start_dir = temp.absolute_path("sub")
        explorer_options = Options(stop_dir=str(temp.absolute_path(".")))

        with patch.object(builtins, "open", wraps=builtins.open) as open_spy:
            # Check read files as cosmiconfig searches for meta config
            explorer = cosmiconfig("foo", **explorer_options.dict())
            meta_config_search_paths = temp.get_spy_path_calls(open_spy)
            assert meta_config_search_paths == [
                "pyproject.toml",
                "pyproject.tml",
                ".config.json",
                ".config.yaml",
                ".config.yml",
            ]
            open_spy.reset_mock()

            # Check read files as cosmiconfig searches for package config
            result = explorer.search(start_dir)
            config_search_paths = temp.get_spy_path_calls(open_spy)
            assert config_search_paths == [
                ".config.yml",
                "sub/.foo-config",
                "sub/.foo.config.yml",
                ".foo-config",
            ]
            assert result == CosmiconfigResult(config={"a": "c"}, filepath=str(file))

    def test_without_placeholder(temp: TempDir):
        temp.create_file(
            ".config.yml",
            'pycosmiconfig:\n  search_places: [".foo-config", ".foo.config.yml"]',
        )
        _run_test(temp)

    def test_with_placeholder(temp: TempDir):
        temp.create_file(
            ".config.yml",
            'pycosmiconfig:\n  search_places: [".{name}-config", ".{name}.config.yml"]',
        )
        _run_test(temp)


def describe_checks_config_in_meta_file():
    @pytest.fixture(autouse=True)
    def current_dir(temp: TempDir):
        temp.create_dir("sub")
        temp.create_file(".foo-config", "a: c")

        current_dir = os.getcwd()
        os.chdir(temp.dir)
        yield current_dir
        os.chdir(current_dir)

    def describe_not_existing():
        def test_sync(temp: TempDir):
            temp.create_file(
                ".config.yml", 'pycosmiconfig:\n  search_places: [".foo-config"]'
            )
            file = temp.absolute_path(".foo-config")
            explorer_options = Options(
                stop_dir=str(temp.absolute_path(".")), ignore_empty_search_places=False
            )

            with patch.object(builtins, "open", wraps=builtins.open) as open_spy:
                # Check read files as cosmiconfig searches for meta config
                explorer = cosmiconfig("foo", **explorer_options.dict())
                meta_config_search_paths = temp.get_spy_path_calls(open_spy)

                assert meta_config_search_paths == [
                    "pyproject.toml",
                    "pyproject.tml",
                    ".config.json",
                    ".config.yaml",
                    ".config.yml",
                ]
                open_spy.reset_mock()

                # Check read files as cosmiconfig searches for package config
                result = explorer.search(str(temp.dir))

                config_search_paths = temp.get_spy_path_calls(open_spy)
                assert config_search_paths == [
                    ".config.yml",
                    ".foo-config",
                ]
                assert result == CosmiconfigResult(
                    config={"a": "c"}, filepath=str(file)
                )

    def describe_existing():
        def test_sync(temp: TempDir):
            temp.create_file(".config.yml", "foo:\n  a: d")
            explorer_options = Options(stop_dir=str(temp.absolute_path(".")))

            explorer = cosmiconfig("foo", **explorer_options.dict())
            # Check read files as cosmiconfig searches for package config
            with patch.object(builtins, "open", wraps=builtins.open) as open_spy:
                result = explorer.search(str(temp.dir))

                config_search_paths = temp.get_spy_path_calls(open_spy)
                assert config_search_paths == [".config.yml"]
                assert result == CosmiconfigResult(
                    config={"a": "d"}, filepath=str(temp.absolute_path(".config.yml"))
                )
