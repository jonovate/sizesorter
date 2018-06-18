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
Represents the values to "decrement" for smaller sizes and increment for larger sizes

Example: 
Say size_chart['XS'] = 0, size_chart['XL'] = 100  and dynamic_operation('XS', 5, 'XL', 10)
Then 2XS would be -5, 3XS would be -10, 2XL would be 110, 3XL would be 120, etc.
"""
dynamic_operation = namedtuple('dynamic_operation',
                               'key_smallest smallest_decrement key_largest largest_increment')

"""Default Dynamic Operation offsets"""
DYNAMIC_OPERATION_DEFAULTS = dynamic_operation('XS', 10, 'XL', 10)

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
'''
class SizeChart():
    """
    Wrapper class for a size chart
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

        self.dynamic_operations = (dynamic_operations if dynamic_operations
                                   else DYNAMIC_OPERATION_DEFAULTS)
        size_chart_shallow = size_chart if size_chart else SIZE_CHART_DEFAULTS        

        assert all([isinstance(v, Size) for v in size_chart_shallow.values()]), \
            'Size Chart dictionary values should be of type Size, otherwise use .from_simple_dict()'
        assert self.dynamic_operations.key_smallest in size_chart_shallow, \
            'key_smallest not in size_chart'
        assert self.dynamic_operations.key_largest in size_chart_shallow, \
            'key_largest not in size_chart'
        assert self.dynamic_operations.smallest_decrement > 0, \
            'smallest_decrement must be positive number'
        assert self.dynamic_operations.largest_increment > 0, \
            'largest_increment must be positive number'
        
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
            'Size Chart dictionary values should be integer'

        size_dict = {key: Size(key, value, key, False) for key, value in simple_dict.items()}     
        return cls(size_dict, dynamic_operations)

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

        :param str x_size: The current x-side which we need to decrease/increase
        :return: The next size down (for smaller) or up (for larger)
        :rtype str
        """
        
        if dynamic_size in [self.dynamic_operations.key_smallest,
                            self.dynamic_operations.key_largest,
                           ]:
            return '2' + dynamic_size
        else:
            return '{}{}'.format(int(dynamic_size[0]) +1, dynamic_size[1:])


    def generate_list(self, length=5):
        """
        Generates a list around the mid-point size. (len//2)
        Will retract from smallest-end first and extend on largest-end first.
        
        :param int length: The length of the size list to generate
            Default - 5
        :return: List of sizes of specified length per formtting options
        :rtype list
        """

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
