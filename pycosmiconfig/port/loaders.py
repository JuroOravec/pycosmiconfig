import importlib
from importlib.util import spec_from_file_location, module_from_spec
import json
from pathlib import Path

import toml
import yaml


# PORT COMMENT: We import from Py files instead of JS files,
#               and the imported Py file must expose a "config" variable.
def load_py(filepath: str, content: str):
    # Try to import file as module
    try:
        module = importlib.import_module(filepath)
        return module.config
    except ModuleNotFoundError:
        pass

    # Otherwise try to import file as python source file
    # See https://stackoverflow.com/a/54956419/9788634
    modulename = Path(filepath).stem
    spec = spec_from_file_location(modulename, filepath)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.config


def load_json(filepath: str, content: str):
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON Error in {filepath}:\n{str(e)}")


def load_yaml(filepath: str, content: str):
    try:
        return yaml.load(content, Loader=yaml.FullLoader)
    except yaml.YAMLError as e:
        raise ValueError(f"YAML Error in {filepath}:\n{str(e)}")


def load_toml(filepath: str, content: str):
    try:
        return toml.loads(content)
    except toml.TomlDecodeError as e:
        raise ValueError(f"TOML Error in {filepath}:\n{str(e)}")
