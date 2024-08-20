# Development Guide

This guide is for Chloris developers / package maintainers.  It is not intended for users of the package.

## Setting up your development environment

```bash
# Install development dependencies
pip install boto3 urllib3 pytest pre-commit twine build lazydocs pydocstyle
# activate pre-commit so that code quality checks are run on every commit
pre-commit install
# install the package in editable mode
pip install -e .
```

## Testing

```bash
# set CHLORIS_REFRESH_TOKEN env variable using valid credentials from app-dev.chloris.earth since tests make real calls to the API.

export CHLORIS_REFRESH_TOKEN='TOKEN'

# run all tests
pytest
# run a specific test
pytest tests/test_utils.py

```

## Building / deploying the package

```bash
# consider updating the version in setup.cfg

# build the package
python -m build

# if you receive errors related to virualenv, try uninstalling it and re-installing it twice via `pip uninstall virtualenv` and then `pip install virtualenv`. This is a known issue pre-commit's virtualenv.

# use docker to test the package in a clean environment
docker run --rm -it -v $(pwd):/sdk python:3.9 bash
cd /sdk
pip install dist/chloris_app_sdk-1.0.11-py3-none-any.whl
python -c "from chloris_app_sdk import ChlorisAppClient; print(ChlorisAppClient)"


# upload the package to pypi
twine upload --skip-existing dist/*
```

### Updating the API documentation

The API documentation is generated from the docstrings in the code using [lazydocs](https://github.com/ml-tooling/lazydocs)  To update the documentation, from the chloris-app-sdk directory run:

```bash
lazydocs --output-path="./docs/" --overview-file="index.md" --src-base-url="https://github.com/chloris-geospatial/chloris-app-sdk/blob/main/" --no-watermark ./src/
```
