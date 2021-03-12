import os

from cpac.utils import ls_newest


def args_before_after(argv, args):
    '''Function to create a mock sys.argv with arguments before
    and one with arguments after the command and its arguments.

    Parameters
    ----------
    argv : str
        the command and its arguments

    args : str
        --platform and --image arguments (if any)

    Returns
    -------
    before : list
        f'cpac {args} {argv}'.split(' ')
    after : list
        f'cpac {argv} {args}'.split(' ')
    '''
    if argv.startswith('cpac'):
        argv = argv.lstrip('cpac').strip()
    if args is not None and len(args):
        before = f'cpac {args} {argv}'.split(' ')
        after = f'cpac {argv} {args}'.split(' ')
    else:
        before = f'cpac {argv}'.split(' ')
        after = before
    return before, after


def set_commandline_args(platform, tag, sep=' '):
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
        if sep != ' ':
            args = args.replace(' ', sep)
    if tag and tag is not None:
        args = args + f' --tag{sep}{tag}'
    return args


def SINGULARITY_OPTION():
    singularity_option = ls_newest(os.getcwd(), ['sif', 'simg'])
    return(f'--image {singularity_option}' if (
        singularity_option is not None
    ) else '--platform singularity')


PLATFORM_ARGS = ['--platform docker', SINGULARITY_OPTION()]
TAGS = [None, 'latest', 'dev-v1.8']
