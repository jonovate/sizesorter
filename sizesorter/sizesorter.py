class SizeSorter:
    """Sorts an iterable by apparal size"""

    def __init__(self, size_chart_values=None):
        pass


    @staticmethod
    def _numeric_to_x(size):
        """Converts a numeric-prefixed size nXS/nXL to X-prefixed size
        Warning: Will convert 1XS to XS (debatable)

        >>> _numeric_to_x('3XS')
        'XXXS'
        >> _numeric_to_x('2XL')
        XXL
        """

        #Boundary checks
        assert(size is not None)
        assert(size[:-2].isnumeric())
        assert(size[-2:] in ['XS','XL'])    #must end in S or L

        numeric, suffix = int(size[:-2]), size[-1]
        return 'X'*numeric + suffix

    @staticmethod
    def _x_to_numeric(size):
        """Converts a X-prefixed size XXS/XXXL to numeric-prefixed size.
        Warning: Will NOT convert XS to 1XS (debatable)
        
        >>> _x_to_numeric('XXS')
        '2XS'
        >> _x_to_numeric('XXXL')
        3XL
        """

        #Boundary checks
        assert(size is not None)
        assert(size.isalpha())
        assert(size[-2:] in ['XS','XL'])    #must end in S or L

        length_x, suffix = len(size[:-1]), size[-2:]   #[:-1] to catch final X
        return (str(length_x) if length_x > 1 else '') + suffix


