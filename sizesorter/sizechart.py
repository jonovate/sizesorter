"""Structure of size charts and values
"""

from collections import namedtuple
from operator import itemgetter
from itertools import cycle

"""Default mapping of sizes"""
SIZE_CHART_DEFAULT = {
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
Represents the values to decrement smaller sizes and increment larger sizes

Example: 
Say size_chart['XS'] = 0, size_chart['XL'] = 100  and x_offset('XS', 5, 'XL', 10)
Then 2XS would be -5, 3XS would be -10, 2XL would be 110, 3XL would be 120, etc.
"""
x_offset = namedtuple('x_offset',
                      'key_smallest smallest_decrement key_largest largest_increment')


class SizeChart():
    """
    Wrapper class for a size chart
    """

    def __init__(self, size_chart=None, x_offsets=None):
        """
        Initializes a size chart wrapper class

        :param dict size_chart: Map of sizes and values
            Default - Uses SIZE_CHART_DEFAULT map
        :param tpl x_offsets: Tuple of (Small,Large) offsets to apply to values less than or
            greater than input values.  
            Default - (1 to decrement XS, +1 to increment XL)
        """
        self.size_chart = size_chart if size_chart else SIZE_CHART_DEFAULT
        self.x_offsets = x_offsets if x_offsets else x_offset('XS', 10, 'XL', 10)

        assert(self.x_offsets.key_smallest in self.size_chart)
        assert(self.x_offsets.key_largest in self.size_chart)
        assert(self.x_offsets.smallest_decrement > 0)
        assert(self.x_offsets.largest_increment > 0)

    def _next_x_offset(self, x_size):
        """
        Returns the next x_offset based on the present value

        :param str x_size: The current x-side which we need to decrease/increase
        :return: The next size down (for smaller) or up (for larger)
        :rtype str
        """

        if x_size in [self.x_offsets.key_smallest, self.x_offsets.key_largest]:
            return '2' + x_size
        else:
            return '{}{}'.format(int(x_size[0]) +1, x_size[1:])


    def generate_list(self, length=5):
        """
        Generates a list around the mid-point size. 
        Will expand/retract from smallest-end first.
        
        :param int length: The length of the size list to generate
            Default - 5
        :return: List of sizes of specified length
        :rtype list
        """

        #Ensure dict key ordering by value
        sorted_sizes = [key for key,value in sorted(self.size_chart.items(), key=itemgetter(1))]
                
        if length < len(sorted_sizes):          #Will need to delete
            begin_end = cycle([0, -1])
            while length < len(sorted_sizes):
                del sorted_sizes[next(begin_end)]       

        elif length > len(sorted_sizes):       #Will need to add
            begin_end = cycle([0, -1])
            while len(sorted_sizes) < length:
                idx = next(begin_end)
                #Increment number on either side as necessary
                next_size = self._next_x_offset(sorted_sizes[idx])
                sorted_sizes.insert(0 if idx == 0 else len(sorted_sizes), next_size)

        return sorted_sizes 


        
