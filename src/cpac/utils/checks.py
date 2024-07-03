"""Functions to check things like the in-container C-PAC version."""

from packaging.version import Version
from semver import VersionInfo

from cpac.backends import Backends


def check_version_at_least(min_version, platform, image=None, tag=None):
    """Check the in-container C-PAC version.

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
        platform = "docker"
    arg_vars = {"platform": platform, "image": image, "tag": tag, "command": "version"}
    version_string = (
        Backends(**arg_vars).run(run_type="version").versions.CPAC.lstrip("v")
    )
    dot_count = version_string.count(".")
    if dot_count > 2:  # noqa: PLR2004
        version_string = version_string.rsplit(".", dot_count - 2)[0]
    return VersionInfo.parse(min_version) <= VersionInfo(
        *(Version(version_string).release)
    )
