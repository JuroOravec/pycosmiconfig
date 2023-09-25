# pycosmiconfig

[![codecov](https://codecov.io/gh/jurooravec/pycosmiconfig/branch/main/graph/badge.svg)](https://codecov.io/gh/jurooravec/pycosmiconfig)

Pycosmiconfig is the Python port of the popular [Cosmiconfig](https://github.com/cosmiconfig/cosmiconfig) package.

> NOTE: Pycosmiconfig uses the same version number as the Cosmiconfig version it's equivalent to. E.g. Pycosmiconfig v8.3.6 == Cosmiconfig v8.3.6
>
> NOTE 2: Pycosmiconfig differs in 3 features from original Cosmiconfig:
>
> 1. Pycosmiconfig prefixes searched property with `tool.` when searching in `pyproject.toml`. So `packageName` becomes `tool.packageName`. On contrary, Cosmiconfig searches for property `packageName` in `package.json`.
> 2. The settings to [configure Pycosmiconfig](#configure-cosmiconfig) are under the `pycosmiconfig` property, instead of Cosmiconfig's `cosmiconfig`.
> 3. Pycosmiconfig has only synchronous operations and the `sync` suffix is omitted. So the two versions below are identical:
>    ```py
>    # Python
>    from pycosmiconfig import cosmiconfig
>    result = cosmiconfig('foo').search()
>    ```
>    ```js
>    // JavaScript
>    const { cosmiconfigSync } = require("cosmiconfig");
>    const result = cosmiconfigSync("foo").search();
>    ```

Cosmiconfig searches for and loads configuration for your program.

It features smart defaults based on conventional expectations.
But it's also flexible enough to search wherever you'd like to search, and load whatever you'd like to load.

By default, Cosmiconfig will start where you tell it to start and search up the directory tree for the following:

- a `[tool.{package}]` property in `pyproject.{toml,tml}`
- a JSON or YAML, extensionless "rc file"
- an "rc file" with the extensions `.json`, `.yaml`, `.yml`, `.toml`, `.tml` or `.py`
- any of the above two inside a `.config` subdirectory
- a `.config.py` file

For example, if your module's name is "myapp", cosmiconfig will search up the directory tree for configuration in the following places:

- a `[tool.myapp]` property in `pyproject.toml` and `pyproject.tml`
- a `.myapprc` file in JSON or YAML format
- a `.myapprc.json`, `.myapprc.yaml`, `.myapprc.yml`, `.myapprc.toml`, `.myapprc.tml`, `.myapprc.py` file
- a `myapprc`, `myapprc.json`, `myapprc.yaml`, `myapprc.yml`, `myapprc.toml`, `myapprc.tml`, `myapprc.py` file inside a `.config` subdirectory
- a `myapp.config.py` file

Cosmiconfig continues to search up the directory tree, checking each of these places in each directory, until it finds some acceptable configuration (or hits the home directory).

## Table of contents

- [Installation](#installation)
- [Usage for tooling developers](#usage-for-tooling-developers)
- [Result](#result)
- [Synchronous API](#synchronous-api)
  - [cosmiconfig()](#cosmiconfig)
  - [explorer.search()](#explorersearch)
  - [explorer.load()](#explorerload)
  - [explorer.clear_load_cache()](#explorerclear_load_cache)
  - [explorer.clear_search_cache()](#explorerclear_search_cache)
  - [explorer.clear_caches()](#explorerclear_caches)
- [CosmiconfigOptions](#cosmiconfigoptions)
  - [search_places](#search_places)
  - [loaders](#loaders)
  - [package_prop](#package_prop)
  - [stop_dir](#stop_dir)
  - [cache](#cache)
  - [transform](#transform)
  - [ignore_empty_search_places](#ignore_empty_search_places)
- [Loading Python modules](#loading-python-modules)
- [Caching](#caching)
- [Usage for end users](#usage-for-end-users)
- [Contributing & Development](#contributing--development)

## Installation

Pip:

```
pip install pycosmiconfig
```

Poetry:

```
poetry add pycosmiconfig
```

Tested in Python 3.8+.

## Usage for tooling developers

_If you are an end user (i.e. a user of a tool that uses cosmiconfig, like `prettier` or `stylelint`),
you can skip down to [the end user section](#usage-for-end-users)._

Create a Cosmiconfig explorer, then either `search` for or directly `load` a configuration file.

```py
from pycosmiconfig import cosmiconfig
# ...
explorer = cosmiconfig(module_name) # E.g. 'foo'

# Search for a configuration by walking up directories.
# See documentation for search, below.
try:
    result = explorer.search()
    # result.config is the parsed configuration object.
    # result.filepath is the path to the config file that was found.
    # result.is_empty is True if there was nothing to parse in the config file.
except Exception as error:
    # Do something constructive.

# Load a configuration directly when you know where it should be.
# The result object is the same as for search.
# See documentation for load, below.
result = explorer.load(path_to_config)
```

## Result

The result object you get from `search` or `load` has the following properties:

- **config:** The parsed configuration object. `None` if the file is empty.
- **filepath:** The path to the configuration file that was found.
- **is_empty:** `True` if the configuration file is empty. This property will not be present if the configuration file is not empty.

## Synchronous API

### cosmiconfig()

```py
from pycosmiconfig import cosmiconfig
exporer = cosmiconfig(module_name[, **cosmiconfig_options])
# E.g.
exporer = cosmiconfig('foo', stop_dir='.', transform=lambda x: x)
```

Creates a _synchronous_ cosmiconfig instance ("explorer") configured according to the arguments, and initializes its caches.

#### module_name

Type: `str`. **Required.**

Your module name. This is used to create the default [`search_places`] and [`package_prop`].

If your [`search_places`] value will include files, as it does by default (e.g. `${module_name}rc`), your `module_name` must consist of characters allowed in filenames. That means you should not use package names, such as `@my-org/my-package`, directly in `module_name`.

**[`CosmiconfigOptions`] are documented below.**
You may not need them, and should first read about the functions you'll use.

### explorer.search()

```py
result = explorer.search([search_from])
# E.g.
result = explorer.search()
result = explorer.search('./configs')
```

Searches for a configuration file. Returns a [result] or `None`, if no configuration file is found.

Let's say your module name is `goldengrahams` so you initialized with `explorer = cosmiconfig('goldengrahams')`.
Here's how your default [`search()`] will work:

- Starting from `os.getcwd()` (or some other directory defined by the `search_from` argument to [`search()`]), look for configuration objects in the following places:
  1. A `tool.goldengrahams` property in a `pyproject.toml` or `pyproject.tml` files.
  2. A `.goldengrahamsrc` file with JSON or YAML syntax.
  3. A `.goldengrahamsrc.json`, `.goldengrahamsrc.yaml`, `.goldengrahamsrc.yml`, `.goldengrahamsrc.toml`, `.goldengrahamsrc.tml`, `.goldengrahamsrc.py` file. (To learn more about how Python files are loaded, see ["Loading Python modules"].)
  4. A `goldengrahamsrc`, `goldengrahamsrc.json`, `goldengrahamsrc.yaml`, `goldengrahamsrc.yml`, `goldengrahamsrc.toml`, `goldengrahamsrc.tml`, `goldengrahamsrc.py` file in the `.config` subdirectory.
  5. A `goldengrahams.config.py` file. (To learn more about how Python files are loaded, see ["Loading Python modules"].)
- If none of those searches reveal a configuration object, move up one directory level and try again.
  So the search continues in `./`, `../`, `../../`, `../../../`, etc., checking the same places in each directory.
- Continue searching until arriving at your home directory (or some other directory defined by the cosmiconfig option [`stop_dir`]).
- For Python files,
- If at any point a parsable configuration is found, [`search()`] returns with the [result].
- If no configuration object is found, [`search()`] returns `None`.
- If a configuration object is found _but is malformed_ (causing a parsing error), [`search()`] throws an error.

**If you know exactly where your configuration file should be, you can use [`load()`], instead.**

**The search process is highly customizable.**
Use the cosmiconfig options [`search_places`] and [`loaders`] to precisely define where you want to look for configurations and how you want to load them.

#### search_from

Type: `str`.
Default: `os.getcwd()`.

A filename.
[`search()`] will start its search here.

If the value is a directory, that's where the search starts.
If it's a file, the search starts in that file's directory.

### explorer.load()

```py
result = explorer.load(load_path)
```

Loads a configuration file. Returns [result] or raises an error if the file does not exist or cannot be loaded.

Use `load` if you already know where the configuration file is and you just need to load it.

```py
explorer.load("load/this/file.json") # Tries to load load/this/file.json.
```

If you load a `pyproject.toml` or `pyproject.tml` file, the result will be derived from whatever property is specified as your [`package_prop`].

NOTE: [`package_prop`] will be prefixed with `tool.`, so if your package name is `mypkg`, and you set `package_prop="mypkg"`, then your `pyproject.toml` should have a `tool.mypkg` property:

```toml
[tool.poetry]
...
[tool.mypkg]
val_a="hello"
world = {
  b = 2
}
```

### explorer.clear_load_cache()

Clears the cache used in [`load()`].

### explorer.clear_search_cache()

Clears the cache used in [`search()`].

### explorer.clear_caches()

Performs both [`clear_load_cache()`] and [`clear_search_cache()`].

## CosmiconfigOptions

Possible options are documented below.

### search_places

Type: `List[str]`.
Default: See below.

An list of places that [`search()`] will check in each directory as it moves up the directory tree.
Each place is relative to the directory being searched, and the places are checked in the specified order.

**Default `search_places`:**

```py
[
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
]
```

Create your own array to search more, fewer, or altogether different places.

Every item in `search_places` needs to have a loader in [`loaders`] that corresponds to its extension.
(Common extensions are covered by default loaders.)
Read more about [`loaders`] below.

`pyproject.toml` and `pyproject.tml` are special values: When they are included in `search_places`, Cosmiconfig will always parse it as TOML and load a property within it, not the whole file.
That property is defined with the [`package_prop`] option, and defaults to your module name.

Examples, with a module named `porgy`:

```py
# Disallow extensions on rc files:
["pyproject.toml", ".porgyrc", "porgy.config.py"]

# Limit the options dramatically:
["pyproject.toml", ".porgyrc"]

# Maybe you want to look for a wide variety of python flavors:
[
  "porgy.config.py",
  "porgy.config.py3",
  "porgy.config.py2",
  # ^^ You will need to designate custom loaders to tell
  # Cosmiconfig how to handle `.py2` and `.py3` files.
]

# Look within a .config/ subdirectory of every searched directory:
[
  "pyproject.toml",
  ".porgyrc",
  ".config/.porgyrc",
  ".porgyrc.json",
  ".config/.porgyrc.json"
]
```

### loaders

Type: `Dict[str, Loader]`.
Default: See below.

A dictionary that maps extensions to the loader functions responsible for loading and parsing files with those extensions.

Cosmiconfig exposes its default loaders on the named export `default_loaders`.

**Default `loaders`:**

```py
from pycosmiconfig import default_loaders

print(default_loaders.items())
# dict_items([
#     ( '.py', <Function: load_py at ...> ),
#     ( '.json', <Function: load_json at ...> ),
#     ( '.yaml', <Function: load_yaml at ...> ),
#     ( '.yml', <Function: load_yaml at ...> ),
#     ( '.toml', <Function: load_toml at ...> ),
#     ( '.tml', <Function: load_toml at ...> ),
#     ( 'noExt', <Function: load_yaml at ...> ),
# ])
```

(YAML is a superset of JSON; which means YAML parsers can parse JSON; which is how extensionless files can be either YAML _or_ JSON with only one parser.)

**If you provide a `loaders` object, your object will be _merged_ with the defaults.**
So you can override one or two without having to override them all.

**Keys in `loaders`** are extensions (starting with a period), or `noExt` to specify the loader for files _without_ extensions, like `.myapprc`.

**Values in `loaders`** are a loader function (described below) whose values are loader functions.

**The most common use case for custom loaders value is to load extensionless `rc` files as strict JSON**, instead of JSON _or_ YAML (the default).
To accomplish that, provide the following `loaders` value:

```py
{
  "noExt": default_loaders[".json"];
}
```

If you want to load files that are not handled by the loader functions Cosmiconfig exposes, you can write a custom loader function or use one from PyPI if it exists.

**Third-party loaders:**

_Do you know of third-party loaders? Open an issue or PR to have it added here._

**Use cases for custom loader function:**

- Allow configuration syntaxes that aren't handled by Cosmiconfig's defaults, like JSON5, INI, or XML.
- Pre-process Python files before deriving the configuration.

**Custom loader functions** have the following signature:

```py
# Sync
def my_loader(filepath: str, content: str) -> Dict | None:
    ...
```

Cosmiconfig reads the file when it checks whether the file exists, so it will provide you with both the file's path and its content.
Do whatever you need to, and return either a configuration object or `None`.
`None` indicates that no real configuration was found and the search should continue.

Examples:

```js
// Allow JSON5 syntax:
{
  '.json': json5_loader
}

// Allow a special configuration syntax of your own creation:
{
  '.special': special_loader
}
```

### package_prop

Type: `str | List[str]`.
Default: `` `{module_name}` ``.

Name of the property in `pyproject.{toml,tml}` to look for.

`package_prop` is prefixed with `tool.` when searching in `pyproject.toml`. So if you set `package_prop` to `"module_name"`, then cosmiconfig will search for `tool.module_name` in `pyproject.toml`.

Use a period-delimited string or an array of strings to describe a path to nested properties.

For example, the value `'my_package.configs.one'` or `['my_package', 'configs', 'one']` will get you the `"one"` value in a `pyproject.toml` like this:

```toml
[tool.poetry]
...
[tool.my_package]
configs = {
  one = 1
}
```

Or this

```toml
[tool.poetry]
...
[tool.my_package.configs]
one = 1
```

If nested property names within the path include periods, you need to use an array of strings. For example, the value `['my_package', 'configs', 'foo.bar', 'baz']` will get you the `"baz"` value in a `pyproject.toml` like this:

```toml
[tool.poetry]
...
[tool.my_package]
configs = {
  "foo.bar" = {
    baz = 2
  }
}
```

If a string includes period but corresponds to a top-level property name, it will not be interpreted as a period-delimited path. For example, the value `'one.two'` will get you the `"three"` value in a `pyproject.toml` like this:

```toml
[tool.poetry]
...
tool."one.two" = "three"
[tool.one]
two = "four"
```

### stop_dir

Type: `str`.
Default: Absolute path to your home directory.

Directory where the search will stop.

### cache

Type: `bool`.
Default: `True`.

If `False`, no caches will be used.
Read more about ["Caching"](#caching) below.

### transform

Type: `(Result) => Result`.

A function that transforms the parsed configuration. Receives the [result].

The reason you might use this option — instead of simply applying your transform function some other way — is that _the transformed result will be cached_. If your transformation involves additional filesystem I/O or other potentially slow processing, you can use this option to avoid repeating those steps every time a given configuration is searched or loaded.

### ignore_empty_search_places

Type: `bool`.
Default: `True`.

By default, if [`search()`] encounters an empty file (containing nothing but whitespace) in one of the [`search_places`], it will ignore the empty file and move on.
If you'd like to load empty configuration files, instead, set this option to `False`.

Why might you want to load empty configuration files?
If you want to throw an error, or if an empty configuration file means something to your program.

## Loading Python modules

The default [`search_places`] include `.py` files. Python files MUST define a `config` top-level variable. This way you don't have to worry about accidentally exposing imported modules and internal variables.

Here is an example config file `{my_module}.config.py`:

```py
# Imports are not exposed
import os

# This value is ignored
some_value_read_from_os = os.name

# Only this config variable will be exposed to Cosmiconfig
config = {
  "name": some_value_read_from_os,
  "indent": 4
}
```

Cosmiconfig attempts to load Python file in two ways. First, it tries to loads the file as a module with [`importlib.import_module`](https://docs.python.org/3/library/importlib.html#importlib.import_module). Hence, you should avoid naming your config files such that their names could conflict with standard python modules, or any packages you've installed, like `json.py`, `toml.py`, etc.

If `importlib.import_module` fails, then the `.py` file is [loaded as a source file](https://stackoverflow.com/a/54956419/9788634).

## Caching

Cosmiconfig uses caching to reduce the need for repetitious reading of the filesystem or expensive transforms. Every new cosmiconfig instance (created with `cosmiconfig()`) has its own caches.

To avoid or work around caching, you can do the following:

- Set the `cosmiconfig` option [`cache`] to `False`.
- Use the cache-clearing methods [`clear_load_cache()`], [`clear_search_cache()`], and [`clear_caches()`].
- Create separate instances of cosmiconfig (separate "explorers").

## Usage for end users

When configuring a tool, you can use multiple file formats and put these in multiple places.

Usually, a tool would mention this in its own README file,
but by default, these are the following places, where `{NAME}` represents the name of the tool:

```
pyproject.toml
pyproject.tml
.{NAME}rc
.{NAME}rc.json
.{NAME}rc.yaml
.{NAME}rc.yml
.{NAME}rc.toml
.{NAME}rc.tml
.{NAME}rc.py
.config/{NAME}rc
.config/{NAME}rc.json
.config/{NAME}rc.yaml
.config/{NAME}rc.yml
.config/{NAME}rc.toml
.config/{NAME}rc.tml
.config/{NAME}rc.py
{NAME}.config.py
```

The contents of these files are defined by the tool.
For example, you can configure prettier to enforce semicolons at the end of the line
using a file named `.config/prettierrc.yml`:

```yaml
semi: true
```

Additionally, you have the option to put a property named after the tool in your `pyproject.toml` file,
with the contents of that property being the same as the file contents.

If the tool is named `{NAME}`, then the property in `pyproject.toml` will be prefixed with `tool.`, so it becomes `tool.{NAME}`:

```toml
[tool.poetry]
...
[tool.my_package]
config_val_a = 1
```

This has the advantage that you can put the configuration of all tools
(at least the ones that use cosmiconfig) in one file.

### Configure Cosmiconfig

You can also add a `tool.pycosmiconfig` key within your `pyproject.toml` file or add a `pycosmiconfig` key to one of the following files
to configure `pycosmiconfig` itself:

```
.config.json
.config.yaml
.config.yml
.config.toml
.config.tml
.config.py
```

The following property is currently actively supported in these places:

```yaml
pycosmiconfig:
  # overrides where configuration files are being searched to enforce a custom naming convention and format
  search_places:
    - .config/{name}.yml
```

> **Note:** Technically, you can overwrite all options described in [cosmiconfigOptions](#cosmiconfigoptions) here,
> but everything not listed above should be used at your own risk, as it has not been tested explicitly.

You can also add more root properties outside the `pycosmiconfig` property
to configure your tools, entirely eliminating the need to look for additional configuration files:

```yaml
pycosmiconfig:
  search_places: []

prettier:
  semi: true
```

## Contributing & Development

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

And please do participate!

[result]: #result
[`load()`]: #explorerload
[`search()`]: #explorersearch
[`clear_load_cache()`]: #explorerclear_load_cache
[`clear_search_cache()`]: #explorerclear_search_cache
[`cosmiconfig()`]: #cosmiconfig
[`clear_caches()`]: #explorerclear_caches
[`package_prop`]: #package_prop
[`cache`]: #cache
[`stop_dir`]: #stop_dir
[`search_places`]: #search_places
[`loaders`]: #loaders
[`cosmiconfigoptions`]: #cosmiconfigoptions
[`explorer.search()`]: #explorersearch
[`explorer.load()`]: #explorerload
["Loading Python modules"]: #loading-python-modules
