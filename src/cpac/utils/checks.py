"""Functions to check things like the in-container C-PAC version."""
from semver import VersionInfo

from cpac.backends import Backends


def check_version_at_least(min_version, platform, image=None, tag=None):
    """Function to check the in-container C-PAC version

    Parameters
    ----------
    min_version : str
        Semantic version

    platform : str or None

    image : str or None

    tag : str or None

    Returns
    -------
    bool
        Is the version at least the minimum version?
    """
    if platform is None:
        platform = 'docker'
    arg_vars = {'platform': platform, 'image': image, 'tag': tag,
                'command': 'version'}
    return VersionInfo.parse(min_version) <= VersionInfo.parse(
        Backends(**arg_vars).run(
            run_type='version').versions.CPAC.lstrip('v'))
