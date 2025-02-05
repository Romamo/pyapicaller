#!/usr/bin/env sh
python -m build
python -m twine upload --skip-existing dist/*