"""Structure of size charts and values
"""

from collections import namedtuple
from copy import deepcopy
from functools import total_ordering
from itertools import cycle

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
        """
        self._key = key
        self._sort_value = sort_value
        self._verbose = verbose if verbose else key
        self._is_dynamic_size = is_dynamic_size

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


    # def next_size(self):
    #     pass


"""Default mapping of sizes to Size objects"""
SIZE_CHART_DEFAULTS = {
    'XS': Size('XS', 0, 'X-Small', True),
    'S':  Size('S',  25, 'Small', False),
    'M':  Size('M',  50, 'Medium', False),
    'L':  Size('L',  75, 'Large', False),
    'XL': Size('XL', 100, 'X-Large', True),
}


"""Minimal mapping of sizes to sort values"""
SIZE_CHART_SIMPLE_EXAMPLE = {
    'XS': 0,
    'S': 25,
    'M': 50,
    'L': 75,
    'XL': 100,
}

"""
Example mapping for Women's Tops
Reference: https://www.express.com/service/custserv.jsp?name=SizeChart
"""
SIZE_CHART_WOMENS_TOPS_EXAMPLE = {
    'XS': 0,
    'S': 4,
    'M': 8,
    'L': 12,
    'XL': 16,
}

"""
Represents the values to "increment" for smaller sizes and "increment" for larger sizes.
Both values will be used in an addition operation.

Example: 
Say size_chart['XS'] = 0, size_chart['XL'] = 100  and dynamic_operation('XS', -5, 'XL', 10)
Then 2XS would be -5, 3XS would be -10, 2XL would be 110, 3XL would be 120, etc.
"""
dynamic_operation = namedtuple('dynamic_operation',
                               'key_smallest smallest_increment key_largest largest_increment')

"""Default Dynamic Operation offsets"""
DYNAMIC_OPERATION_DEFAULTS = dynamic_operation('XS', -10, 'XL', 10)

"""
Default Size Chart formatting options
    
    verbose: Whether to display verbose name or just short value
    dynamic_size_verbose: Whether to display dynamics (XS/XL/etc.) sizes as verbose or not
    dynmic_size_formatter: Formatting method for the small/larger dynamic sizes 
"""
SIZE_CHART_FORMAT_DEFAULTS = {'verbose': False,
                              'dynamic_size_verbose': False,
                              'x_size_formatter': str,
                             }


####TODO
'''
 ---Verbose
 ---N vs X
 ---Formatter
 ---Single Ended Dynamic Size
'''
class SizeChart():
    """
    Wrapper class for a size chart

    Principle: Size should only be visible externally from constructor, otherwise remain internal
    """

    def __init__(self, size_chart=None, dynamic_operations=None, *, formatting_options=None):
        """
        Initializes a size chart wrapper class

        :param dict size_chart: Map of sizes and values
            Default - Uses SIZE_CHART_DEFAULTS map
        :param tpl dynamic_operations: Tuple of dynamic keys and offsets to apply to dynamic values
            Default - Uses DYNAMIC_OPERATION_DEFAULTS
        :param dict formatting_options: Formatting options for the Size Chart
            Default - Uses SIZE_CHART_FORMAT_DEFAULTS map
        """
        self._dynamic_size_cache = True

        self.dynamic_operations = (dynamic_operations if dynamic_operations
                                   else DYNAMIC_OPERATION_DEFAULTS)
        size_chart_shallow = size_chart if size_chart else SIZE_CHART_DEFAULTS        

        assert all([isinstance(v, Size) for v in size_chart_shallow.values()]), \
            'Size Chart dictionary values should be of type Size, otherwise use .from_simple_dict()'
        assert self.dynamic_operations.key_smallest in size_chart_shallow, \
            'key_smallest not in size_chart'
        assert self.dynamic_operations.key_largest in size_chart_shallow, \
            'key_largest not in size_chart'
        assert self.dynamic_operations.smallest_increment < 0, \
            'smallest_increment must be a negative number'
        assert self.dynamic_operations.largest_increment > 0, \
            'largest_increment must be a positive number'
        
        self.size_chart = deepcopy(size_chart_shallow)
        #Make sure they're set in case user forgot
        self.size_chart[self.dynamic_operations.key_smallest].is_dynamic_size = True
        self.size_chart[self.dynamic_operations.key_largest].is_dynamic_size = True

        #Deepcopy since they can be overwritten after instantiation
        self.formatting_options = deepcopy(formatting_options if formatting_options
                                           else SIZE_CHART_FORMAT_DEFAULTS)

    @classmethod
    def from_simple_dict(cls, simple_dict, dynamic_operations=None):
        """
        Builds a SizeChart instance from a simple map of Size key to sort value

        :param tpl dynamic_operations: Tuple of dynamic keys and offsets to apply to dynamic values
            Default - Uses DYNAMIC_OPERATION_DEFAULTS
        """
        from numbers import Number
        assert all([isinstance(v, Number) for v in simple_dict.values()]), \
            'Size Chart dictionary values should be Numbers'

        size_dict = {key: Size(key, value, key, False) for key, value in simple_dict.items()}     
        return cls(size_dict, dynamic_operations)

    def __len__(self):
        """
        Returns the length of the Size Chart
        
        :return: The length of the Size Chart
        :rtype int
        """
        return len(self.size_chart)

    def _is_dynamic_key_format(self, size_key):
        """
        Determines whether the key would be considered a dynamic key based on the Dynamic Operations
        configuration passed in on instantion.
        
        :param str size_key: The size to look up in our chart.
        :returns Whether the key would be considered a dynamic key based on its format
        :rtype bool
        """
        return size_key.endswith(self.dynamic_operations.key_smallest) or \
               size_key.endswith(self.dynamic_operations.key_largest)

    def _split_dynamic_key(self, size_key):
        """
        Splits a potential dynamic key into prefix and dynamic key suffix.

        :param str size_key: The size to look up in our chart.
        :returns A tuple of prefix and dynamic key suffix.  Suffix will be None if not dynamic key.
        :rtype tuple(str, str)
        """
        if not self._is_dynamic_key_format(size_key):
            return (size_key, None)

        suff_len = (len(self.dynamic_operations.key_smallest)
                   if size_key.endswith(self.dynamic_operations.key_smallest)
                   else len(self.dynamic_operations.key_largest))

        prefix = size_key[:-suff_len]
        return (prefix if prefix not in ['0','1'] else '', size_key[-suff_len:])

    def _generate_dynamic_size(self, size_key):
        """Calculates a dynamic Size based on the key and the dynamic_operation of the Chart.
        
        :str size_key str: The Dynamic Key to generate a Size from
        :return The generated Dynamic Size
        :rtype Size
        """
        prefix, suffix = self._split_dynamic_key(size_key)
        base_suffix = self.size_chart[suffix]

        int_prefix = (int(prefix) - 1 if prefix else 0)
        sort_value = base_suffix.sort_value
        if int_prefix:  #Not empty
            sort_value += int_prefix * (self.dynamic_operations.smallest_increment
                                        if suffix == self.dynamic_operations.key_smallest
                                        else self.dynamic_operations.largest_increment)
        else:
            size_key = base_suffix.key

        verbose = prefix + base_suffix.verbose

        return Size(size_key, sort_value, verbose, True)
                    

    def _get_size(self, size_key):
        """
        Retrieves the size and/or generates it if does not exist

        :param str size_key: The size to look up in our chart.
        :return: The Size object
        :rtype Size
        
        :raises ValueError: If an invalid non-dynamic size is passed in. ('4L' or 'X')
        """
        is_dynamic_size = self._is_dynamic_key_format(size_key)
        
        size = self.size_chart.get(size_key)
        is_new = size is None

        if is_new and is_dynamic_size:
            size = self._generate_dynamic_size(size_key)
        elif is_new and not is_dynamic_size:   
            #Let exception be thrown to caller if not valid (ie: '4L')
            size = Size(size_key, float(size_key), size_key, False)
        
        if is_new and self._dynamic_size_cache:
            self.size_chart[size_key] = size
        
        return size

    def disable_dynamic_size_cache(self):
        """
        Disables saving of generated dynamic sizes into Size Chart (Enabled by Default)
        """
        self._dynamic_size_cache = False        

    def set_formatting_options(self, formatting_options):
        """
        Override the Formatting options for the Size Chart
        
        :param dict formatting_options: Formatting options for the Size Chart
        """

        #In case only single option is passed in, we merge
        self.formatting_options.update(formatting_options)
        
    def _next_dynamic_operation(self, dynamic_size):
        """
        Returns the next dynamic size based on the present value and formatting options

        :param str dynamic_size: The current x-side which we need to decrease/increase
        :return: The next size down (for smaller) or up (for larger)
        :rtype str
        """
        
        if dynamic_size in [self.dynamic_operations.key_smallest,
                            self.dynamic_operations.key_largest,
                           ]:
            return '2' + dynamic_size
        else:
            return '{}{}'.format(int(dynamic_size[0]) +1, dynamic_size[1:])
        
    def generate_list(self, length=len(SIZE_CHART_DEFAULTS)):
        """
        Generates an ordered specific-sized list, pivoted around the mid-point size. (len//2)
        Will retract from smallest-end first and extend on largest-end first.
        
        :param int length: The length of the size list to generate
            Default - len(SIZE_CHART_DEFAULTS) (5)
        :return: List of sizes of specified length per formtting options
        :rtype list
        """
        if length is None:  #For Pytest parameter hack
            length = len(SIZE_CHART_DEFAULTS)

        #Ensure dict key ordering by value (dunders overriden in Size class @total_ordering)
        sorted_sizes = [skey for skey,_ in sorted(self.size_chart.items(),
                                                  key=lambda d: d[1])]
 
        if length < len(sorted_sizes):          #Will need to delete
            begin_end = cycle([0, -1])      #Retract from small-end first
            while length < len(sorted_sizes):
                del sorted_sizes[next(begin_end)]       

        elif length > len(sorted_sizes):       #Will need to add
            begin_end = cycle([-1, 0])      #Extend on large-end first
            while len(sorted_sizes) < length:
                idx = next(begin_end)
                #Increment number on either side as necessary
                next_size = self._next_dynamic_operation(sorted_sizes[idx])
                sorted_sizes.insert(0 if idx == 0 else len(sorted_sizes), next_size)

        return sorted_sizes

    def generate_list_range(self, key_smallest, key_largest):
        """
        Generates an ordered list of specified Sizes between the two ranges (inclusive).
        Per Formatting Options.

        :param str key_smallest: The start Size of the list
        :param str key_largest: The end Size in the list
        :return: List of sizes in the range
        :rtype list
        """

        #Ensure dict key ordering by value (dunders overriden in Size class @total_ordering)
        sorted_sizes = [skey for skey,_ in sorted(self.size_chart.items(),
                                                  key=lambda d: d[1])]

        return sorted_sizes 
