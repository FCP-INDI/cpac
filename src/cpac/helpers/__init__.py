'''Hepler functions for cpac Python package.'''
import re


def get_extra_arg_value(extra_args, argument):
    '''Function to parse passed-through arguments and get their values

    Parameters
    ----------
    extra_args : list

    argument : str

    Returns
    -------
    value : str

    Examples
    --------
    >>> get_extra_arg_value([
    ...     '--preconfig=fmriprep-options',
    ...     '--data_config_file=/configs/data_config_regtest.yml',
    ...     '--participant_ndx=3'], 'preconfig')
    'fmriprep-options'
    >>> get_extra_arg_value([
    ...     '--preconfig=fmriprep-options',
    ...     '--data_config_file=/configs/data_config_regtest.yml',
    ...     '--participant_ndx 3'], 'participant_ndx')
    '3'
    '''
    pattern = r'^\-*' + argument + r'([=\s]{1}.*)$'

    for index, item in enumerate(extra_args):
        if re.match(pattern, item) is not None:
            for sep in {'=', ' '}:
                if sep in item:
                    return item.split(sep, 1)[1]
            if len(extra_args) > index:
                return extra_args[index + 1]


__all__ = ['get_extra_arg_value']
