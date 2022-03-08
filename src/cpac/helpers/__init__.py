'''Hepler functions for cpac Python package.'''
import re
from itertools import chain


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
    # pattern = r'^\-*' + argument + r'([=\s]{1}.*)$'

    extra_args = list(chain.from_iterable([
        re.split('[=\s]', arg) for arg in extra_args]))

    for index, item in enumerate(extra_args):
        if item.startswith('-') and item.lstrip('-') == argument:
            return extra_args[index + 1]

__all__ = ['get_extra_arg_value']
