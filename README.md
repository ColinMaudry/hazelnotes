# hazelnotes

Managing notes in the command line

Editing notes in HedgeDoc

Storing note metadata in SQLite.    

## How to

### Install

```shell
pip install hazelnotes
```

### Package and publish to pypi.org

1. Configure `~/.pypirc` ([official documentation](https://packaging.python.org/en/latest/specifications/pypirc/))
2. Check that the app metadata is correct in `./pyproject.toml`
3. Package the app:

```shell
# Make sure build is up to date
python3 -m pip install --upgrade build

# Package the app
python3 -m build

# The app is build and packaged in `./dist`
```

3. Publish the app on pypi.org:

```shell
# Make sure Twine is installed and up to date
python3 -m pip install --upgrade twine

# Publish the app
python3 -m twine upload --repository pypi dist/*
```