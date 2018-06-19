###
import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parentdir not in sys.path:
    sys.path.insert(0, parentdir)
###

import pytest
from sizesorter import (
     Size,
     dynamic_operation,
     SizeChart,
     SIZE_CHART_DEFAULTS,
     DYNAMIC_OPERATION_DEFAULTS,
     SIZE_CHART_FORMAT_DEFAULTS
    )
from sizesorter.sizechart import SIZE_CHART_SIMPLE_EXAMPLE, SIZE_CHART_WOMENS_TOPS_EXAMPLE

# Doesn't work with Paramterized Test Cases. https://github.com/pytest-dev/pytest/issues/349
# @pytest.fixture(scope='module',
#                 params=[(SIZE_CHART_DEFAULTS, None),
#                         (SIZE_CHART_DEFAULTS, DYNAMIC_OPERATION_DEFAULTS)])
# def default_size_chart(request):
#     return SizeChart(*request.param)

@pytest.fixture(scope='module')
def default_size_chart():
    return SizeChart(SIZE_CHART_DEFAULTS, None)

@pytest.fixture(scope='module')
def default_size_chart_and_dynamic_operations():
    return SizeChart(SIZE_CHART_DEFAULTS, DYNAMIC_OPERATION_DEFAULTS)

@pytest.fixture(scope='module')
def custom_size_chart():
    return SizeChart.from_simple_dict( {'A': 1, 'B': 2, 'C': 3},
                                       dynamic_operation('A', 5, 'C', 5)
                                     )

def test_class():
    size_chart = SizeChart()
    assert id(size_chart) > 0

    assert len(SIZE_CHART_DEFAULTS) == 5     # Make sure length hasn't changed ('XS' -> 'XL')
    assert len(size_chart) == len(SIZE_CHART_DEFAULTS)

    x_offsets = dynamic_operation('XS', 1, 'XL', 1)
    assert id(x_offsets)

    size = next(iter(size_chart.size_chart.values()))
    assert str(size) == '{} ({})'.format(size.verbose, size.key)

def test_invalid_chart():
    
    bad_size_chart = {'J': Size('J', 10)}
    bad_offset = dynamic_operation('A', 0, 'Z', -1)

    with pytest.raises(AssertionError):
        SizeChart.from_simple_dict(bad_size_chart)    #Wrong Dict value
        
        SizeChart.from_simple_dict(bad_size_chart, bad_offset)   #Missing A
        bad_size_chart['A'] = Size('A', 1)

        SizeChart.from_simple_dict(bad_size_chart, bad_offset)   #Missing Z
        bad_size_chart['Z'] = Size('Z', 26)
        
        SizeChart.from_simple_dict(bad_size_chart, bad_offset)     #Bad decrement
        new_bad_offset = dynamic_operation('A', 50, 'Z', -1)
        
        SizeChart.from_simple_dict(bad_size_chart, new_bad_offset)  #Bad decrement

def test_invalid_simple_chart():
    
    bad_chart = {'J': 10}
    bad_offset = dynamic_operation('A', 0, 'Z', -1)

    with pytest.raises(AssertionError):
        SizeChart(bad_chart)                          #Wrong Dict Value
        
        SizeChart(bad_chart, bad_offset)                         #Missing A
        bad_chart['A'] = 1

        SizeChart(bad_chart, bad_offset)                         #Missing Z
        bad_chart['Z'] = 26
        
        SizeChart(bad_chart, bad_offset)                           #Bad decrement
        new_bad_offset = dynamic_operation('A', 50, 'Z', -1)
        
        SizeChart(bad_chart, new_bad_offset)                        #Bad increment

@pytest.mark.parametrize("size_chart, dynamic_key, expected", 
    [(default_size_chart, 'M', False),
     (default_size_chart, 'XS', True),
     (default_size_chart, '2XS', True),
     (default_size_chart, '15XS', True),
     (default_size_chart, 'XL', True),
     (default_size_chart, '3XL', True),
     (default_size_chart, '10XL', True),
     (default_size_chart_and_dynamic_operations, 'M', False),
     (default_size_chart_and_dynamic_operations, 'XS', True),
     (default_size_chart_and_dynamic_operations, '2XS', True),
     (default_size_chart_and_dynamic_operations, '15XS', True),
     (default_size_chart_and_dynamic_operations, 'XL', True),
     (default_size_chart_and_dynamic_operations, '3XL', True),
     (default_size_chart_and_dynamic_operations, '10XL', True),
     (custom_size_chart, 'B', False),
     (custom_size_chart, 'A', True),
     (custom_size_chart, '3A', True),
     (custom_size_chart, '14A', True),
     (custom_size_chart, 'C', True),
     (custom_size_chart, '5C', True),
     (custom_size_chart, '100C', True),
    ],)
def test_is_dynamic_key_format(size_chart, dynamic_key, expected):
    size_chart()._is_dynamic_key_format(dynamic_key) == expected

    #TODO - Test Verbose and XXL keys    

@pytest.mark.parametrize("size_chart, dynamic_key, expected_tpl", 
    [(default_size_chart, 'M', ('M', None)),
     (default_size_chart, 'XS', ('', 'XS')),
     (default_size_chart, '2XS', ('2', 'XS')),
     (default_size_chart, '15XS', ('15', 'XS')),
     (default_size_chart, 'XL', ('', 'XL')),
     (default_size_chart, '3XL', ('3', 'XL')),
     (default_size_chart, '10XL', ('10', 'XL')),
     (default_size_chart_and_dynamic_operations, 'M', ('M', None)),
     (default_size_chart_and_dynamic_operations, 'XS', ('', 'XS')),
     (default_size_chart_and_dynamic_operations, '2XS', ('2', 'XS')),
     (default_size_chart_and_dynamic_operations, '15XS', ('15', 'XS')),
     (default_size_chart_and_dynamic_operations, 'XL', ('', 'XL')),
     (default_size_chart_and_dynamic_operations, '3XL', ('3', 'XL')),
     (default_size_chart_and_dynamic_operations, '10XL', ('10', 'XL')),
     (custom_size_chart, 'B', ('B', None)),
     (custom_size_chart, 'A', ('', 'A')),
     (custom_size_chart, '3A', ('3', 'A')),
     (custom_size_chart, '14A', ('14', 'A')),
     (custom_size_chart, 'C', ('', 'C')),
     (custom_size_chart, '5C', ('5', 'C')),
     (custom_size_chart, '100C', ('100', 'C')),
    ],
    )
def test_split_dynamic_key(size_chart, dynamic_key, expected_tpl):
    assert size_chart()._split_dynamic_key(dynamic_key) == expected_tpl

    #TODO - Test Verbose and XXL keys    

@pytest.mark.xfail
def test_dynamic_size_cache(default_size_chart):
    chart_size = len(default_size_chart)
    default_size_chart.get_size('2XS')    #Size should increase by 1
    chart_size += 1
    assert chart_size == len(default_size_chart)   
    
    default_size_chart.disable_dynamic_size_cache()
    default_size_chart.get_size('2XL')
    assert chart_size == len(default_size_chart)  #Size should have staid the same

@pytest.mark.xfail
def test_get_size(default_size_chart):
    default_size_chart.get_size('M')
    assert 'M' == default_size_chart.get_size('M').key

    xl_size = default_size_chart.get_size('XL')
    assert 'XL' == xl_size.key
    assert SIZE_CHART_DEFAULTS['XL'].sort_value == xl_size.sort_value

    xs3_size = default_size_chart.get_size('3XS')
    assert '3XS' == xs3_size.key
    expected_val = SIZE_CHART_DEFAULTS['XS'].sort_value - (2*DYNAMIC_OPERATION_DEFAULTS.smallest_decrement)
    assert expected_val == xs3_size.sort_value

    xl2_size = default_size_chart.get_size('2XL')
    assert '2XL' == xl2_size.key
    assert SIZE_CHART_DEFAULTS['XL'].sort_value + DYNAMIC_OPERATION_DEFAULTS.largest_increment == \
        xl2_size.sort_value
    assert xl_size.sort_value + DYNAMIC_OPERATION_DEFAULTS.largest_increment == xl2_size.sort_value

    #TODO - Test Verbose and XXL keys

@pytest.mark.parametrize("size_chart, list_size, expected", 
    [(default_size_chart, 1, ['M']),
     (default_size_chart, 2, ['M','L']),
     (default_size_chart, 3, ['S','M','L']),
     (default_size_chart, 5, ['XS','S','M','L','XL']),
     (default_size_chart, None, ['XS','S','M','L','XL']),
     (default_size_chart, 6, ['XS','S','M','L', 'XL','2XL']),
     (default_size_chart, 7, ['2XS','XS','S','M','L','XL','2XL']),
     (default_size_chart, 8, ['2XS','XS','S','M','L','XL','2XL','3XL']),
     (default_size_chart_and_dynamic_operations, 1, ['M']),
     (default_size_chart_and_dynamic_operations, 2, ['M','L']),
     (default_size_chart_and_dynamic_operations, 3, ['S','M','L']),
     (default_size_chart_and_dynamic_operations, 5, ['XS','S','M','L','XL']),
     (default_size_chart_and_dynamic_operations, None, ['XS','S','M','L','XL']),
     (default_size_chart_and_dynamic_operations, 6, ['XS','S','M','L', 'XL','2XL']),
     (default_size_chart_and_dynamic_operations, 7, ['2XS','XS','S','M','L','XL','2XL']),
     (default_size_chart_and_dynamic_operations, 8, ['2XS','XS','S','M','L','XL','2XL','3XL']),
     (custom_size_chart, 1, ['B']),
     (custom_size_chart, 2, ['B','C']),
     (custom_size_chart, 3, ['A','B','C']),
     (custom_size_chart, 5, ['2A','A','B','C','2C']),
     (custom_size_chart, None, ['2A','A','B','C','2C']),
     (custom_size_chart, 7, ['3A','2A','A','B','C','2C','3C']),
    ],
    )
def test_generate_list(size_chart, list_size, expected):

    #Generate list is supposed to remove from left first for smaller, and add to right for larger
    assert size_chart().generate_list(list_size) == expected

    #TODO - Test Verbose and XXL keys
    #TODO - Test Single-Ended

def test_generate_list_range(default_size_chart):

    list_M = default_size_chart.generate_list_range('M', 'M')
    #assert ['M'] == list_M

    # list_2 = size_chart.generate_list(2)
    # assert ['M', 'L'] == list_2

    # list_3 = size_chart.generate_list(3)
    # assert ['S', 'M', 'L'] == list_3

    # list_5 = size_chart.generate_list(5)
    # assert ['XS','S','M','L','XL'] == list_5

    # list_6 = size_chart.generate_list(6)
    # assert ['XS','S','M','L','XL', '2XL'] == list_6

    # list_7 = size_chart.generate_list(7)
    # assert ['2XS','XS','S','M','L','XL','2XL'] == list_7

    # list_8 = size_chart.generate_list(8)
    # assert ['2XS','XS','S','M','L','XL','2XL', '3XL'] == list_8
