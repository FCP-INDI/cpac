'''Constants for tests'''
# pylint: disable=invalid-name
TAGS = [None, 'latest', 'nightly']


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
    argv = single_space(argv).strip()
    args = single_space(args).strip()
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
        args += f' --platform{sep}{platform.lower()} '
    if tag and tag is not None:
        args = args + f' --tag{sep}{tag} '
    return args


def single_space(string):
    '''Function to remove spaces from a string

    Parameters
    ----------
    string : str

    Returns
    -------
    string : str
    '''
    while '  ' in string:
        string = string.replace('  ', ' ')
    return string
