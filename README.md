# hazelnotes

Managing notes in the command line

Editing notes in HedgeDoc

Storing note metadata in SQLite.    

## How to

### Install from pypi.org

```shell
pip install hazelnotes
```

### Run it

The installation command has added `hazelnotes` to your PATH. You can run it from command line like so:

```
hazelnotes --help
```

### Test it

`pytest` sets an environment variable when run, `PYTEST_CURRENT_TEST`. If the environment variable is set, the 
alternative "test" configuration is loaded from `config.toml`. The test directory is deleted at the and of the tests.

```
pytest
```

### Package and publish to pypi.org (self reminder FTW)

1. Configure `~/.pypirc` ([official documentation](https://packaging.python.org/en/latest/specifications/pypirc/))
2. Check that the app metadata is correct in `./pyproject.toml`
3. Install `flit` ([documentation](https://flit.pypa.io))
3. Package the app:

```shell
flit build

# The app is build and packaged in `./dist`
```

3. Publish the app on pypi.org:

```shell
# Make sure Twine is installed and up to date
python3 -m pip install --upgrade twine

# Publish the app
python3 -m twine upload --repository pypi dist/*
```