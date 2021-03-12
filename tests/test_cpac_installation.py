from pip._internal.utils.misc import get_installed_distributions
from setuptools.config import read_configuration


def test_requirements():
    requirements = {
        'setup.cfg': requirements_list(read_configuration(
                'setup.cfg'
            )['options']['install_requires']
        )
    }
    with open('requirements.txt', 'r') as req:
        requirements['requirements.txt'] = requirements_list(
            req.readlines()
        )
    for req in requirements['requirements.txt']:
        if req.package.lower() != 'setuptools':
            assert package_in_list(
                req, requirements['setup.cfg']
            ), (
                f'package {req} is in requirements.txt '
                'but not in setup.cfg'
            )
            assert package_in_list(
                req, requirements_list(get_installed_distributions())
            ), (
                f'package {req} is in requirements.txt '
                'but not installed'
            )


def test_version():
    from cpac import __version__
    assert __version__ != 'undefined', f'version is {__version__}'


class Requirement():
    def __init__(self, requirement):
        package = str(requirement).rstrip().split(' ')
        self.package = package[0]
        self.version = {
            "==": package[1]
        } if len(package) == 2 else {
            package[i]: package[i+1] for i in range(len(package)) if i % 2
        }

    def __repr__(self):
        return ' '.join([
            f'{self.package}',
            ', '.join([
                f'{key} {self.version[key]}' for key in self.version
            ])
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
            p.package.lower() for p in version_list
        ]
    )


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
