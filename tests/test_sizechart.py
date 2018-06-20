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
                                       dynamic_operation('A', -5, 'C', 5)
                                     )

def test_class():
    size_chart = SizeChart()
    assert id(size_chart) > 0

    assert len(SIZE_CHART_DEFAULTS) == 5     # Make sure length hasn't changed ('XS' -> 'XL')
    assert len(size_chart) == len(SIZE_CHART_DEFAULTS)

    x_offsets = dynamic_operation('XS', -1, 'XL', 1)
    assert id(x_offsets)

    size = next(iter(size_chart.size_chart.values()))
    assert str(size) == '{} ({})'.format(size.verbose, size.key)

@pytest.mark.parametrize("test_tpl", 
    list({
            1: 'Size',
            2: 'key_smallest',
            3: 'key_largest',
            4: 'smallest_increment',
            5: 'largest_increment',
           }.items()))
def test_invalid_chart(test_tpl):
    
    bad_size_chart = {'H': 4, 'J': Size('J', 10)}
    bad_offset = dynamic_operation('A', 0, 'Z', 25)

    with pytest.raises(AssertionError) as ae:

        if test_tpl[0] == 1:
            SizeChart(bad_size_chart)    #Wrong Dict value
        
        del(bad_size_chart['H'])
        if test_tpl[0] == 2:
            SizeChart(bad_size_chart, bad_offset)   #Missing A

        bad_size_chart['A'] = Size('A', 1)
        if test_tpl[0] == 3:            
            SizeChart(bad_size_chart, bad_offset)   #Missing Z

        bad_size_chart['Z'] = Size('F', 26) 
        if test_tpl[0] == 4:                      
            SizeChart(bad_size_chart, bad_offset)     #Bad decrement

        new_bad_offset = dynamic_operation('A', -50, 'Z', 0)
        if test_tpl[0] == 5:
            SizeChart(bad_size_chart, new_bad_offset)  #Bad increment


    assert str(ae.value).find(test_tpl[1]) > -1

@pytest.mark.parametrize("test_tpl", 
    list({
            1: 'Size',
            2: 'key_smallest',
            3: 'key_largest',
            4: 'smallest_increment',
            5: 'largest_increment',
           }.items()))
def test_invalid_simple_chart(test_tpl):
    
    bad_chart = {'J': 10, 'K': Size('K', 11)}
    bad_offset = dynamic_operation('A', 25, 'Z', 25)

    with pytest.raises(AssertionError) as ae:
        
        if test_tpl[0] == 1:
            SizeChart.from_simple_dict(bad_chart)                                    #Wrong Dict Value
        
        del(bad_chart['K'])
        if test_tpl[0] == 2:            
            SizeChart.from_simple_dict(bad_chart, bad_offset)                         #Missing A
                
        bad_chart['A'] = 1
        if test_tpl[0] == 3:
            SizeChart.from_simple_dict(bad_chart, bad_offset)                         #Missing Z
        
        bad_chart['Z'] = 26
        if test_tpl[0] == 4: 
            SizeChart.from_simple_dict(bad_chart, bad_offset)                           #Bad decrement
        
        new_bad_offset = dynamic_operation('A', -50, 'Z', -50)
        if test_tpl[0] == 5: 
            SizeChart.from_simple_dict(bad_chart, new_bad_offset)                        #Bad increment
        
    assert str(ae.value).find(test_tpl[1]) > -1

@pytest.mark.parametrize("size_chart, dynamic_key, expected", 
    [(default_size_chart, 'M', False),
     (default_size_chart, 'XS', True),
     (default_size_chart, '1XS', True),
     (default_size_chart, '2XS', True),
     (default_size_chart, '15XS', True),
     (default_size_chart, '1XL', True),
     (default_size_chart, 'XL', True),
     (default_size_chart, '3XL', True),
     (default_size_chart, '10XL', True),
     (default_size_chart_and_dynamic_operations, 'M', False),
     (default_size_chart_and_dynamic_operations, 'XS', True),
     (default_size_chart_and_dynamic_operations, '1XS', True),
     (default_size_chart_and_dynamic_operations, '2XS', True),
     (default_size_chart_and_dynamic_operations, '15XS', True),
     (default_size_chart_and_dynamic_operations, 'XL', True),
     (default_size_chart_and_dynamic_operations, '1XL', True),
     (default_size_chart_and_dynamic_operations, '3XL', True),
     (default_size_chart_and_dynamic_operations, '10XL', True),
     (custom_size_chart, 'B', False),
     (custom_size_chart, 'A', True),
     (custom_size_chart, '1A', True),
     (custom_size_chart, '3A', True),
     (custom_size_chart, '14A', True),
     (custom_size_chart, '1C', True),
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
     (default_size_chart, '1XS', ('', 'XS')),
     (default_size_chart, '2XS', ('2', 'XS')),
     (default_size_chart, '15XS', ('15', 'XS')),
     (default_size_chart, 'XL', ('', 'XL')),
     (default_size_chart, '1XL', ('', 'XL')),
     (default_size_chart, '3XL', ('3', 'XL')),
     (default_size_chart, '10XL', ('10', 'XL')),
     (default_size_chart_and_dynamic_operations, 'M', ('M', None)),
     (default_size_chart_and_dynamic_operations, 'XS', ('', 'XS')),
     (default_size_chart_and_dynamic_operations, '1XS', ('', 'XS')),
     (default_size_chart_and_dynamic_operations, '2XS', ('2', 'XS')),
     (default_size_chart_and_dynamic_operations, '15XS', ('15', 'XS')),
     (default_size_chart_and_dynamic_operations, 'XL', ('', 'XL')),
     (default_size_chart_and_dynamic_operations, '1XL', ('', 'XL')),
     (default_size_chart_and_dynamic_operations, '3XL', ('3', 'XL')),
     (default_size_chart_and_dynamic_operations, '10XL', ('10', 'XL')),
     (custom_size_chart, 'B', ('B', None)),
     (custom_size_chart, 'A', ('', 'A')),
     (custom_size_chart, '1A', ('', 'A')),
     (custom_size_chart, '3A', ('3', 'A')),
     (custom_size_chart, '14A', ('14', 'A')),
     (custom_size_chart, 'C', ('', 'C')),
     (custom_size_chart, '1C', ('', 'C')),
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

@pytest.mark.parametrize("size_chart, size_key, expected_tpl", 
    [(default_size_chart, 'XS', ('XS', 0, 'X-Small', True)),
     (default_size_chart, '1XS', ('XS', 0, 'X-Small', True)),
     (default_size_chart, '2XS', ('2XS', -10, '2X-Small', True)),
     (default_size_chart, '15XS', ('15XS', -140, '15X-Small', True)),
     (default_size_chart, 'XL', ('XL', 100, 'X-Large', True)),
     (default_size_chart, '1XL', ('XL', 100, 'X-Large', True)),
     (default_size_chart, '3XL', ('3XL', 120, '3X-Large', True)),
     (default_size_chart, '10XL', ('10XL', 190, '10X-Large', True)),
     (default_size_chart_and_dynamic_operations, 'XS', ('XS', 0, 'X-Small', True)),
     (default_size_chart_and_dynamic_operations, '1XS', ('XS', 0, 'X-Small', True)),
     (default_size_chart_and_dynamic_operations, '2XS', ('2XS', -10, '2X-Small', True)),
     (default_size_chart_and_dynamic_operations, '15XS', ('15XS', -140, '15X-Small', True)),
     (default_size_chart_and_dynamic_operations, 'XL', ('XL', 100, 'X-Large', True)),
     (default_size_chart_and_dynamic_operations, '1XL', ('XL', 100, 'X-Large', True)),
     (default_size_chart_and_dynamic_operations, '3XL', ('3XL', 120, '3X-Large', True)),
     (default_size_chart_and_dynamic_operations, '10XL', ('10XL', 190, '10X-Large', True)),
     (custom_size_chart, 'A', ('A', 1, 'A', True)),
     (custom_size_chart, '1A', ('A', 1, 'A', True)),
     (custom_size_chart, '3A', ('3A', -9, '3A', True)),
     (custom_size_chart, '14A', ('14A', -64, '14A', True)),
     (custom_size_chart, 'C', ('C', 3, 'C', True)),
     (custom_size_chart, '1C', ('C', 3, 'C', True)),
     (custom_size_chart, '5C', ('5C', 23, '5C', True)),
     (custom_size_chart, '100C', ('100C', 498, '100C', True)),
    ],
    )
def test_generate_dynamic_size(size_chart, size_key, expected_tpl):
    assert isinstance(size_chart()._generate_dynamic_size(size_key), Size)

    assert size_chart()._generate_dynamic_size(size_key).key == expected_tpl[0]
    assert size_chart()._generate_dynamic_size(size_key).sort_value == expected_tpl[1]
    assert size_chart()._generate_dynamic_size(size_key).verbose == expected_tpl[2]
    assert size_chart()._generate_dynamic_size(size_key).is_dynamic_size == expected_tpl[3]

    #TODO - Test XXL keys    
    
@pytest.mark.xfail
def test_get_size(default_size_chart):
    default_size_chart.get_size('M')
    assert 'M' == default_size_chart.get_size('M').key

    xl_size = default_size_chart.get_size('XL')
    assert 'XL' == xl_size.key
    assert SIZE_CHART_DEFAULTS['XL'].sort_value == xl_size.sort_value

    xs3_size = default_size_chart.get_size('3XS')
    assert '3XS' == xs3_size.key
    expected_val = SIZE_CHART_DEFAULTS['XS'].sort_value + \
        (2*DYNAMIC_OPERATION_DEFAULTS.smallest_increment)
    assert expected_val == xs3_size.sort_value

    xl2_size = default_size_chart.get_size('2XL')
    assert '2XL' == xl2_size.key
    assert SIZE_CHART_DEFAULTS['XL'].sort_value + DYNAMIC_OPERATION_DEFAULTS.largest_increment == \
        xl2_size.sort_value
    assert xl_size.sort_value + DYNAMIC_OPERATION_DEFAULTS.largest_increment == xl2_size.sort_value

    #TODO - Test Verbose and XXL keys


@pytest.mark.parametrize("default_size_chart, test_tpl",
    [(default_size_chart, ('5M', 'string to float')),
     (default_size_chart, ('B', 'string to float')),
    ])    
def test_get_size_exception(default_size_chart, test_tpl):
    
    with pytest.raises(ValueError) as ve:
        assert default_size_chart()._get_size(test_tpl[0])
        
    assert str(ve.value).find(test_tpl[1]) > -1

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


if __name__ == "__main__":
    pytest.main()
