"""Test if cpac is installed as expected"""
try:
    from importlib.metadata import distribution, distributions, \
        PackageNotFoundError, PathDistribution
except ModuleNotFoundError:
    from importlib_metadata import distribution, distributions, \
        PackageNotFoundError, PathDistribution
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def test_requirements():
    """Test that requirements are listed in config and in requirements.txt
    and that they are all installed."""
    config_file = 'pyproject.toml'
    with open(config_file, 'rb') as _pyproject:
        requirements = {
            config_file: requirements_list(
                tomllib.load(_pyproject)['project']['dependencies'])}
    with open('requirements.txt', 'r', encoding='utf-8') as req:
        requirements['requirements.txt'] = requirements_list(
            req.readlines())
    for req in requirements['requirements.txt']:
        if req.package.lower() != 'setuptools':
            assert package_in_list(
                req, requirements[config_file]), (
                f'package {req} is in requirements.txt '
                f'but not in {config_file}')
            failure_message = (f'package {req} is in requirements.txt '
                               'but not installed')
            try:
                failure_message += ' '.join([
                    ';', str(req.package),
                    str(distribution(req.package).version), 'installed'])
            except PackageNotFoundError:
                pass
            assert package_in_list(
                req, requirements_list(distributions())), failure_message


def test_version():
    """Check that version is set"""
    from cpac import __version__  # pylint: disable=import-outside-toplevel
    assert __version__ != 'undefined', f'version is {__version__}'


class Requirement():
    """Parse various types of requirements into a type with a
    'package' attribute and a 'version' attribute"""
    # pylint: disable=too-few-public-methods
    def __init__(self, requirement):
        if isinstance(requirement, PathDistribution):
            self.package = requirement.name
            self.version = {'==': requirement.version}
        else:
            package = str(requirement).rstrip().split(' ')
            versions = len(package)
            try:
                if len(package):
                    self.package = package[0]
                    self.version = {
                        "==": package[1]} if versions == 2 else {
                        package[i]: package[i + 1] for i in range(versions) if
                        ((i % 2) and (i + 1 < versions))}
            except IndexError as index_error:
                raise IndexError(f'{package}') from index_error

    def __repr__(self):
        return ' '.join([
            f'{self.package}',
            ', '.join([
                f'{key} {self.version[key]}' for key in self.version])
        ]).strip()


def package_in_list(package, version_list):
    """
    Helper function to check if a case-insensitive named package
    is included in a list of Requirements

    Parameters
    ----------
    package: str

    version_list: list

    Returns
    -------
    bool
    """
    return(
        package.package.lower() in [
            p.package.lower() for p in version_list])


def requirements_list(requirements):
    """
    Helper function to split coerce a list of requirements into
    a list of Requirements

    Parameters
    ----------
    requirements: list
        list of requirment strings

    Returns
    -------
    list
        list of Requirements
    """
    return([Requirement(r) for r in requirements])
