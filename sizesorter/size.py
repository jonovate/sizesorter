"""
Structure representing a Size
"""

from functools import total_ordering

@total_ordering
class Size():
    """
    Represents the struture for a Size object
    """

    def __init__(self, key, sort_value, verbose=None, is_dynamic_size=False):
        """
        Initializes a Size object for the given value

        :param str key: The key/base of the size
        :param int sort_value: The sort value of the 
        :param str Verbose:
            Default - Will be set to key if not specified
        :param boolean is_dynamic_size: Whether the size is a dynamic size (ie: X-Size)
            Default - False
        :param boolean is_dynamic_size: Whether the size is a dynamic size (ie: X-Size)
            Default - False
        """
        self._key = key
        self._sort_value = sort_value
        self._verbose = verbose if verbose else key
        self._is_dynamic_size = is_dynamic_size

        self._previous_size_key = self._next_size_key = None

    def __str__(self):
        return '{} ({})'.format(self._verbose, self._key)

    def __lt__(self, other):
        return self.sort_value < other.sort_value

    @property
    def key(self):
        return self._key

    @property
    def sort_value(self):
        return self._sort_value

    @property
    def verbose(self,):
        return self._verbose

    @property
    def as_numeric_size(self, x):
        pass

    @property
    def as_formatted_size(self, x):
        pass

    @property
    def is_dynamic_size(self):
        return self._is_dynamic_size
    @is_dynamic_size.setter
    def is_dynamic_size(self, is_dynamic_size):
        self._is_dynamic_size = is_dynamic_size

    #Double-Linked list type logic
    @property
    def previous_size_key(self):
        return self._previous_size_key
    @previous_size_key.setter
    def previous_size_key(self, previous_size_key):
        self._previous_size_key = previous_size_key

    @property
    def next_size_key(self):
        return self._next_size_key
    @next_size_key.setter
    def next_size_key(self, next_size_key):
        self._next_size_key = next_size_key
