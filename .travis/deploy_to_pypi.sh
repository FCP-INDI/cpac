python setup.py sdist bdist_wheel
twine upload dist/* -u $GITHUB_USERNAME -p $PYPI_PASSWORD