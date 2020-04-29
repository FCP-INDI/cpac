from cpac import dist_name
from warnings import warn

class Permission_mode():
    """
    Class to overload comparison operators to compare file permissions levels.

    'rw' > 'w' > 'r'
    """
    defined_modes = {'rw', 'w', 'r', 'ro'}

    def __init__(self, fs_str):

        self.mode = fs_str.mode if isinstance(
            fs_str,
            Permission_mode
        ) else 'r' if fs_str=='ro' else fs_str
        self.defined = self.mode in Permission_mode.defined_modes
        self._warn_if_undefined()

    def __repr__(self):
        return(self.mode)

    def __gt__(self, other):
        for permission in (self, other):
            if(permission._warn_if_undefined()):
                return(NotImplemented)

        if self.mode=='rw':
            if other.mode in {'w', 'r'}:
                return(True)
        elif self.mode=='w' and other.mode=='r':
            return(True)

        return(False)

    def __ge__(self, other):
        for permission in (self, other):
            if(permission._warn_if_undefined()):
                return(NotImplemented)

        if self.mode==other.mode or self>other:
            return(True)

        return(False)

    def __lt__(self, other):
        for permission in (self, other):
            if(permission._warn_if_undefined()):
                return(NotImplemented)

        if self.mode=='r':
            if other.mode in {'w', 'rw'}:
                return(True)
        elif self.mode=='r' and other.mode=='w':
            return(True)

        return(False)

    def __le__(self, other):
        for permission in (self, other):
            if(permission._warn_if_undefined()):
                return(NotImplemented)

        if self.mode==other.mode or self<other:
            return(True)

        return(False)

    def _warn_if_undefined(self):
        if not self.defined:
            warn(
                f'\'{self.mode}\' is not a fully-configured permission '
                f'level in {dist_name}. Configured permission levels are '
                f'''{", ".join([
                    f"'{mode}'" for mode in Permission_mode.defined_modes
                ])}''',
                UserWarning
            )
            return(True)
        return(False)