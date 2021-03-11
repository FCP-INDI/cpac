import os

from cpac.utils import ls_newest


def set_commandline_args(platform, tag):
    '''Function to turn pytest commandline options into mock
    cpac commandline option strings

    Parameters
    ----------
    platform : string

    tag : string

    Returns
    -------
    args : string
    '''
    args = ''
    if platform is not None:
        if platform.lower() == 'docker':
            args = args + PLATFORM_ARGS[0]
        elif platform.lower() == 'singularity':
            args = args + PLATFORM_ARGS[1]
    if tag and tag is not None:
        args = args + f' --tag {tag}'
    return args


def SINGULARITY_OPTION():
    singularity_option = ls_newest(os.getcwd(), ['sif', 'simg'])
    return(f'--image {singularity_option}' if (
        singularity_option is not None
    ) else '--platform singularity')


PLATFORM_ARGS = ['--platform docker', SINGULARITY_OPTION()]
TAGS = [None, 'latest', 'dev-v1.8']
