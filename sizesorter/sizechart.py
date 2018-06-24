"""
Structure of size charts and values
"""

from collections import namedtuple
from copy import deepcopy
from itertools import cycle

from .size import Size

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
 ---Baby Size/Toddler Size/Kids Size
 ---Dynamic Size prefix increments

 decorator, generators
'''
class SizeChart():
    """
    Wrapper class for a size chart

    Principle: Size should only be visible externally from constructor, otherwise remain internal
    """

    def __init__(self, size_chart=None, dynamic_operations=None, *, formatting_options=None):
        """
        Initializes a size chart wrapper class.
        The Dynamic Size Cache is disabled by default.

        :param dict size_chart: Map of sizes and values
            Default - Uses SIZE_CHART_DEFAULTS map
        :param tpl dynamic_operations: Tuple of dynamic keys and offsets to apply to dynamic values
            Default - Uses DYNAMIC_OPERATION_DEFAULTS
        :param dict formatting_options: Formatting options for the Size Chart
            Default - Uses SIZE_CHART_FORMAT_DEFAULTS map

        :raise ValueError: If the dynamic_operation keys are not in the Size Chart or invalid
            (smaller_ should be negative, greater_ should be positive)
        """
        self._dynamic_size_cache = False

        self.dynamic_operations = (dynamic_operations if dynamic_operations
                                   else DYNAMIC_OPERATION_DEFAULTS)
        size_chart_shallow = size_chart if size_chart else SIZE_CHART_DEFAULTS        

        if not all([isinstance(v, Size) for v in size_chart_shallow.values()]):
            raise ValueError('Size Chart dictionary values should be of type Size,'
                             'otherwise use .from_simple_dict()')
        if not self.dynamic_operations.key_smallest in size_chart_shallow:
            raise ValueError('key_smallest not in size_chart')
        if not self.dynamic_operations.key_largest in size_chart_shallow:
            raise ValueError('key_largest not in size_chart')
        if not self.dynamic_operations.smallest_increment < 0:
            raise ValueError('smallest_increment must be a negative number')
        if not self.dynamic_operations.largest_increment > 0:
            raise ValueError('largest_increment must be a positive number')
        
        self.size_chart = deepcopy(size_chart_shallow)

        #Setup double-linked pointers
        previous_obj = None
        for key,size_obj in sorted(self.size_chart.items(), key=lambda d: d[1]):

            if previous_obj:
                previous_obj.next_size_key = key                    #previous obj's next
                size_obj.previous_size_key = previous_obj.key       #this obj's previous
            previous_obj = size_obj

            #Make sure the dynamic_size property is set in case user forgot
            #  at same time, need to set double-linked pointers
            if key == self.dynamic_operations.key_smallest:
                size_obj.is_dynamic_size = True
                size_obj.previous_size_key = '2' + key
            elif key == self.dynamic_operations.key_largest:
                size_obj.is_dynamic_size = True
                size_obj.next_size_key = '2' + key 

        #Deepcopy since they can be overwritten after instantiation
        self.formatting_options = deepcopy(formatting_options 
                                           if formatting_options
                                           else SIZE_CHART_FORMAT_DEFAULTS)

    @classmethod
    def from_simple_dict(cls, simple_dict, dynamic_operations=None):
        """
        Builds a SizeChart instance from a simple map of Size key to sort value

        :param tpl dynamic_operations: Tuple of dynamic keys and offsets to apply to dynamic values
            Default - Uses DYNAMIC_OPERATION_DEFAULTS
        
        :raise ValueError: If simple_dict contains any values that are not Numbers
        :raise ValueError: If simple_dict contains any values that are not Numbers
        """
        from numbers import Number
        if not all([isinstance(v, Number) for v in simple_dict.values()]):
            raise ValueError('Size Chart dictionary values should be Numbers')

        size_dict = {key: Size(key, value, key, False) for key, value in simple_dict.items()}     
        return cls(size_dict, dynamic_operations)

    def __len__(self):
        """
        Returns the length of the Size Chart
        
        :return: The length of the Size Chart
        :rtype int
        """
        return len(self.size_chart)

    def _is_potentially_dynamic(self, size_key):
        """
        Determines whether the key could be considered (no guarantee) a dynamic key based on the
        Dynamic Operations configuration passed in on instantiation.
        
        :param str size_key: The size to look up in our chart.
        :returns Whether the key would be considered a dynamic key based on its format
        :rtype bool
        """
        return size_key.endswith(self.dynamic_operations.key_smallest) or \
               size_key.endswith(self.dynamic_operations.key_largest)

    def _parse_size_key(self, size_key):
        """
        Splits a potential dynamic key into prefix and dynamic key suffix.

        :param str size_key: The size to look up in our chart.
        :returns A tuple representing the prefix, suffix, whether it's a dynamic key. 
                Prefix will also be empty if not dynamic key.
        :rtype tuple(str, str, bool)

        :raises ValueError: If the key is not parsable (invalid characters, etc.)
        """
        if not self._is_potentially_dynamic(size_key):
            return ('', size_key, False)

        suff_len = (len(self.dynamic_operations.key_smallest)
                   if size_key.endswith(self.dynamic_operations.key_smallest)
                   else len(self.dynamic_operations.key_largest))

        prefix = size_key[:-suff_len]
        if not(prefix == '' or prefix.isalnum()):
            raise ValueError('Prefix of Dynamic Key must be a positive number or not set')

        return (prefix if prefix not in ['1'] else '', size_key[-suff_len:], True)

    def _generate_dynamic_size(self, size_key):
        """
        Calculates a dynamic Size based on the key and the dynamic_operation of the Chart.
        
        :str size_key str: The Dynamic Key to generate a Size from
        :return The generated Dynamic Size
        :rtype Size

        :raises ValueError: If the key is not parsable (invalid characters, etc.) or it it wasn't
            a dynamic size per Size Chart
        """

        """INLINE"""
        def __prefix_to_key(prefix, base_suffix, is_smaller_dynamic):
            if prefix == 0:
                return (base_suffix.next_size_key
                       if is_smaller_dynamic  #If 0XS, then we want S which is next
                       else base_suffix.previous_size_key)   #If 0XL, we want L which is previous
            if prefix == 1:
                return base_suffix.key
            return str(prefix) + base_suffix.key

        """INLINE"""
        def __set_previous_next(size, int_prefix, base_suffix, is_smaller_dynamic):
            #int_prefix is current prefix - 1
            up_key = __prefix_to_key(int_prefix+2, base_suffix, is_smaller_dynamic)
            down_key = __prefix_to_key(int_prefix, base_suffix, is_smaller_dynamic)

            if is_smaller_dynamic:
                dynamic_size.previous_size_key = up_key
                dynamic_size.next_size_key = down_key
            else:
                dynamic_size.previous_size_key = down_key
                dynamic_size.next_size_key = up_key

        prefix, suffix, is_dynamic_size = self._parse_size_key(size_key)
        if not is_dynamic_size:
            raise ValueError('Suffix is not defined as dynamic size')
        base_suffix = self.size_chart[suffix]

        is_smaller_dynamic = (True if suffix == self.dynamic_operations.key_smallest else False)

        sort_value = base_suffix.sort_value
        int_prefix = (int(prefix) - 1 if prefix else 0)
        if int_prefix:  #Not empty
            sort_value += int_prefix * (self.dynamic_operations.smallest_increment
                                        if is_smaller_dynamic
                                        else self.dynamic_operations.largest_increment)
        else:
            size_key = base_suffix.key

        verbose = prefix + base_suffix.verbose

        dynamic_size = Size(size_key, sort_value, verbose, True)
        __set_previous_next(dynamic_size, int_prefix, base_suffix, is_smaller_dynamic)

        return dynamic_size

    def _size_key_to_size(self, size_key):
        """
        Converts the size_key to a size

        :param str size_key: The size key to convert to a size
        :return: A tuple of Size object and whether it existed in Chart already
        :rtype tpl(Size,bool)
        
        :raises ValueError: If an invalid dynamic size is passed in.
            Examples: '-5XL', '+3XL', '4L' {non-dynamic} or 'X' {invalid size}
        """
        is_dynamic_size = self._is_potentially_dynamic(size_key)
        
        size = self.size_chart.get(size_key)
        is_new = size is None

        if is_new:
            if is_dynamic_size:
                size = self._generate_dynamic_size(size_key)
            elif size_key.isnumeric():
                size = Size(size_key, float(size_key), size_key, False)
            else:
                raise ValueError('Base size not defined and/or not dynamic')

        return (size,is_new)

    def get_or_create_size(self, size_key):
        """
        Retrieves the size and/or generates it if does not exist

        note:: Will add to Dynamic Size cache if Enabled.

        :param str size_key: The size to look up in our chart.
        :return: The Size object
        :rtype Size
        
        :raises ValueError: If an invalid dynamic size is passed in.
            Examples: '-5XL', '+3XL', '4L' {non-dynamic} or 'X' {invalid size}
        """
        size, is_new = self._size_key_to_size(size_key)
        
        if is_new and self._dynamic_size_cache:
            self.size_chart[size_key] = size
    
        return size

    def enable_dynamic_size_cache(self):
        """
        Disables saving of generated dynamic sizes into Size Chart (Disabled by Default).
        Useful if you think you will be using it often.
        """
        self._dynamic_size_cache = True        

    def set_formatting_options(self, formatting_options):
        """
        Override the Formatting options for the Size Chart
        
        :param dict formatting_options: Formatting options for the Size Chart
        """

        #In case only single option is passed in, we merge
        self.formatting_options.update(formatting_options)

    def generate_lengthed_list(self, list_length=len(SIZE_CHART_DEFAULTS)):
        """
        Generates an ordered specific-sized list, pivoted around the mid-point size. (len//2)
        Will retract from smallest-end first and extend on largest-end first.

        note:: Does not alter Size Chart or Dynamic Cache since we don't want to delete.
        warning:: If Dynamic Size Cache has been enabled, you should not be using this as it can
            result in smallest leaning or largest leaning results (due to mid-point having changed)
        
        :param int list_length: The length of the size list to generate
            Default - len(SIZE_CHART_DEFAULTS) (5)
        :return: List of sizes of specified length per formatting options
        :rtype list
        """
        if list_length is None:  #For Pytest parameter hack
            list_length = len(SIZE_CHART_DEFAULTS)
 
        ##TODO - Move this to Sorter class??
        sorted_sizes = [key for key,_ in sorted(self.size_chart.items(), key=lambda d: d[1])]

        mid = (len(sorted_sizes)-1) // 2
        addl_needed = abs(list_length - len(sorted_sizes))
        #Give priority to right side
        left_cnt, right_cnt = addl_needed // 2, -(-addl_needed // 2)  #Floor, Ceiling
        
        if list_length < len(sorted_sizes):          #Will need to delete - so reverse counts
            sorted_sizes = sorted_sizes[right_cnt:mid+1] + \
            sorted_sizes[mid+1:len(sorted_sizes)-left_cnt]

        elif list_length > len(sorted_sizes):       #Will need to add
            for x in range(0, max(left_cnt,right_cnt)):
                if x < left_cnt:
                    left = self._size_key_to_size(sorted_sizes[0])
                    sorted_sizes.insert(0, left[0].previous_size_key)
                right = self._size_key_to_size(sorted_sizes[-1])
                sorted_sizes.insert(len(sorted_sizes), right[0].next_size_key)

        return sorted_sizes

    def generate_range_iter(self, start_range_key, end_range_key):
        """
        Generates iterable of specified Sizes between the two ranges (inclusive).
        Per Formatting Options.

        :param str start_range_key: The start size (key) of the list
        :param str end_range_key: The end size (key) of the list
        :return: List of sizes in the range
        :rtype list

        :raises ValueError: If the base of the range keys don't exist in the Size Chart
        """

        #validate and get anchors
        start_size = self.get_or_create_size(start_range_key)
        self.get_or_create_size(end_range_key)  #To ensure its valid

        next_size = start_size
        yield start_size.key

        while next_size.key != end_range_key:
            next_size = self.get_or_create_size(next_size.next_size_key)
            yield next_size.key

    def generate_range_list(self, start_range_key, end_range_key):
        """
        Generates an ordered list of specified Sizes between the two ranges (inclusive).
        Per Formatting Options.

        :param str start_range_key: The start Size of the list
        :param str end_range_key: The end Size in the list
        :return: List of sizes in the range
        :rtype list

        :raises ValueError: If the base of the range keys don't exist in the Size Chart
        """
        return list(self.generate_range_iter(start_range_key, end_range_key))
