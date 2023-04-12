"""Test if cpac is installed as expected"""
try:
    from importlib.metadata import distribution, distributions, \
        PackageNotFoundError, PathDistribution
except ModuleNotFoundError:
    from importlib_metadata import distribution, distributions, \
        PackageNotFoundError, PathDistribution
from operator import eq, ge, gt
from re import match
from semver import Version
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def _version(version: str) -> 'Version':
    """Take a Pythonic version string and return a semver version"""
    try:
        return Version(*[match(r'^\d+', part).group(0) for part in
                        version.split('.')])
    except (AttributeError, IndexError):
        return None


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
            try:
                assert package_in_list(
                    req, requirements_list(distributions())), failure_message
            except AssertionError as assertion_error:
                installed = requirements_list(distributions())
                raise AssertionError('\n'.join([f'installed: {installed}', f'required: {requirements["requirements.txt"]}'])) from assertion_error
                print(installed)
                print(requirements['requirements.txt'])
                docker_installed = installed[
                    [_p.package.lower() for _p in installed].index('docker')]
                docker_required = requirements['requirements.txt'][
                    [_p.package.lower() for _p in
                     requirements['requirements.txt']].index('docker')]
                print(docker_installed)
                print(docker_installed.package)
                print(docker_installed.operator)
                print(docker_installed.version)
                print(docker_required.package)
                print(docker_required.operator)
                print(docker_required.version)
                raise assertion_error


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
            self.operator = '=='
            self.version = _version(requirement.version)
        else:
            package = str(requirement).rstrip().split(' ')
            versions = len(package)
            try:
                if versions:
                    self.package = package[0]
                if versions == 2:
                    self.operator = '=='
                    self.version = _version(package[1])
                else:
                    self.operator = []
                    self.version = []
                    for i in range(versions - 2):
                        self.operator.append(package[i + 1])
                        self.version.append(package[i + 2])
                        package[i]: _version(package[i + 2])
                if len(self.operator) == 1 and len(self.version) == 1:
                    self.operator = self.operator[0]
                    self.version = self.version[0]
            except IndexError as index_error:
                raise IndexError(f'{package}') from index_error

    def __eq__(self, other: 'Requirement') -> bool:
        if not (self.version and other.version):
            # if at least one version unspecified
            return True
        if self.operator != '==' and other.operator == '==':
            # flip the direction if self isn't pinned
            return other == self
        operators = {'==': eq, '>': gt, '>=': ge}
        if other.operator == '~=':
            return (self.version >= other.version
                    ) and (self.version < other.version.replace(
                           patch=0).next_version('minor'))
        if other.operator in operators:
            return operators[other.operator](self.version, other.version)
        return False

    def __repr__(self):
        return str(self)

    def __str__(self):
        if isinstance(self.operator, list):
            return ' '.join([
                self.package, ', '.join([
                    ' '.join([
                        self.operator[i], self.version[i]]) for i in
                        range(len(self.operator))])])
        return ' '.join([self.package, self.operator, str(self.version)
                         ]).strip()


def package_in_list(package, version_list):
    """
    Helper function to check if a case-insensitive named package
    is included in a list of Requirements

    Parameters
    ----------
    package : str

    version_list : list

    Returns
    -------
    bool
    """
    return package.package.lower() in [
        p.package.lower() for p in version_list]


def requirements_list(requirements):
    """
    Helper function to split coerce a list of requirements into
    a list of Requirements

    Parameters
    ----------
    requirements : list
        list of requirment strings

    Returns
    -------
    req_list : list
        list of Requirements
    """
    prelist = [Requirement(r) for r in requirements]
    req_list = []
    for req in prelist:
        if isinstance(req.operator, list):
            for i, operator in enumerate(req.operator):
                req_list.append(Requirement(' '.join([
                    req.package, operator, str(req.version[i])])))
        else:
            req_list.append(req)
    return req_list
