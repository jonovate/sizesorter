"""
Worker module class for sorting sizes
"""

class SizeSorter:
    """
    Sorts an iterable by apparal size
    """

    def __init__(self, size_chart_values=None):
        pass


    @staticmethod
    def _numeric_to_x(size):
        """
        Converts a numeric-prefixed extreme size nXS/nXL to X-prefixed size
        
        note:: Will convert 1XS to XS (debatable)

        :param str size: The extreme size with numeric prefix
        :return: The extreme size as X-prefix
        :rtype str

        >>> _numeric_to_x('3XS')
        'XXXS'
        >> _numeric_to_x('2XL')
        XXL
        """

        #Boundary checks
        assert size is not None, 'Must be valid size'
        assert size[:-2].isnumeric(), 'Size must be numeric'
        assert size[-2:] in ['XS','XL'], 'Size must end in XS/XL'   #TODO

        numeric, suffix = int(size[:-2]), size[-1]
        return 'X'*numeric + suffix

    @staticmethod
    def _x_to_numeric(size):
        """
        Converts a X-prefixed extreme size XXS/XXXL to numeric-prefixed size.
        
        note:: Will NOT convert XS to 1XS (debatable)
        
        :param str size: The extreme size with X-prefix
        :return: The extreme size as numeric prefix
        :rtype str

        >>> _x_to_numeric('XXS')
        '2XS'
        >> _x_to_numeric('XXXL')
        3XL
        """

        #Boundary checks
        assert size is not None, 'Must be valid size'
        assert size.isalpha(), 'Size must be all alpha characters'
        assert size[-2:] in ['XS','XL'], 'Size must end in XS/XL'   #TODO

        length_x, suffix = len(size[:-1]), size[-2:]   #[:-1] to catch final X
        return (str(length_x) if length_x > 1 else '') + suffix


