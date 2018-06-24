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

@pytest.mark.parametrize("size_chart, size_key, expected_tpl", 
    [(default_size_chart, 'XS', ('2XS', 'S')),
     (default_size_chart, 'S', ('XS', 'M')),
     (default_size_chart, 'M', ('S','L')),
     (default_size_chart, 'L', ('M', 'XL')), 
     (default_size_chart, 'XL', ('L','2XL')),
    ],)
def test_class_default_double_pointers(size_chart, size_key, expected_tpl):
    size = size_chart().size_chart[size_key]
    assert size.previous_size_key == expected_tpl[0]
    assert size.next_size_key == expected_tpl[1]

@pytest.mark.parametrize("test_case_id, expected_tpl", 
    [(1, (ValueError, 'Size')),
     (2, (ValueError, 'key_smallest')),
     (3, (ValueError, 'key_largest')),
     (4, (ValueError, 'smallest_increment')),
     (5, (ValueError, 'largest_increment')),
    ],)
def test_invalid_chart(test_case_id, expected_tpl):
    
    bad_size_chart = {'H': 4, 'J': Size('J', 10)}
    bad_offset = dynamic_operation('A', 0, 'Z', 25)

    with pytest.raises(expected_tpl[0]) as ee:

        if test_case_id == 1:
            SizeChart(bad_size_chart)                           #Wrong Dict value
        
        del(bad_size_chart['H'])
        if test_case_id == 2:
            SizeChart(bad_size_chart, bad_offset)               #Missing A

        bad_size_chart['A'] = Size('A', 1)
        if test_case_id == 3:            
            SizeChart(bad_size_chart, bad_offset)               #Missing Z

        bad_size_chart['Z'] = Size('F', 26) 
        if test_case_id == 4:                      
            SizeChart(bad_size_chart, bad_offset)               #Bad decrement

        new_bad_offset = dynamic_operation('A', -50, 'Z', 0)
        if test_case_id == 5:
            SizeChart(bad_size_chart, new_bad_offset)           #Bad increment

    assert str(ee.value).find(expected_tpl[1]) > -1

@pytest.mark.parametrize("test_case_id, expected_tpl", 
    [(1, (ValueError, 'Size')),
     (2, (ValueError, 'key_smallest')),
     (3, (ValueError, 'key_largest')),
     (4, (ValueError, 'smallest_increment')),
     (5, (ValueError, 'largest_increment')),
    ],)
def test_invalid_simple_chart(test_case_id, expected_tpl):
    
    bad_chart = {'J': 10, 'K': Size('K', 11)}
    bad_offset = dynamic_operation('A', 25, 'Z', 25)

    with pytest.raises(expected_tpl[0]) as ee:
        
        if test_case_id == 1:
            SizeChart.from_simple_dict(bad_chart)                       #Wrong Dict Value
        
        del(bad_chart['K'])
        if test_case_id == 2:            
            SizeChart.from_simple_dict(bad_chart, bad_offset)          #Missing A
                
        bad_chart['A'] = 1
        if test_case_id == 3:
            SizeChart.from_simple_dict(bad_chart, bad_offset)           #Missing Z
        
        bad_chart['Z'] = 26
        if test_case_id == 4: 
            SizeChart.from_simple_dict(bad_chart, bad_offset)           #Bad decrement
        
        new_bad_offset = dynamic_operation('A', -50, 'Z', -50)
        if test_case_id == 5: 
            SizeChart.from_simple_dict(bad_chart, new_bad_offset)        #Bad increment
        
    assert str(ee.value).find(expected_tpl[1]) > -1

@pytest.mark.parametrize("size_chart, size_key, expected_tpl", 
    [(default_size_chart, 'M', (False)),
     (default_size_chart, 'XS', (True)),
     (default_size_chart, '1XS', (True)),
     (default_size_chart, '2XS', (True)),
     (default_size_chart, '-2XS', (True)),  #debatable
     (default_size_chart, '15XS', (True)),
     (default_size_chart, '1XL', (True)),
     (default_size_chart, 'XL', (True)),
     (default_size_chart, '3XL', (True)),
     (default_size_chart, '+3XL', (True)), #debatable
     (default_size_chart, '10XL', (True)),
     (default_size_chart_and_dynamic_operations, 'M', (False)),
     (default_size_chart_and_dynamic_operations, 'XS', (True)),
     (default_size_chart_and_dynamic_operations, '1XS', (True)),
     (default_size_chart_and_dynamic_operations, '2XS', (True)),
     (default_size_chart_and_dynamic_operations, '-2XS', (True)), #debatable
     (default_size_chart_and_dynamic_operations, '15XS', (True)),
     (default_size_chart_and_dynamic_operations, 'XL', (True)),
     (default_size_chart_and_dynamic_operations, '1XL', (True)),
     (default_size_chart_and_dynamic_operations, '3XL', (True)),
     (default_size_chart_and_dynamic_operations, '+3XL', (True)),  #debatable
     (default_size_chart_and_dynamic_operations, '10XL', (True)),
     (custom_size_chart, 'B', (False)),
     (custom_size_chart, 'A', (True)),
     (custom_size_chart, '1A', (True)),
     (custom_size_chart, '3A', (True)),
     (custom_size_chart, '-3A', (True)),  #debatable
     (custom_size_chart, '14A', (True)),
     (custom_size_chart, '1C', (True)),
     (custom_size_chart, 'C', (True)),
     (custom_size_chart, '5C', (True)),
     (custom_size_chart, '+5C', (True)),  #debatable
     (custom_size_chart, '100C', (True)),
    ],)
def test_is_potentially_dynamic(size_chart, size_key, expected_tpl):
    assert size_chart()._is_potentially_dynamic(size_key) == expected_tpl#[0]

    #TODO - Test Verbose and XXL keys    

@pytest.mark.parametrize("size_chart, size_key, expected_tpl", 
    [(default_size_chart, 'M', ('', 'M', False)),
     (default_size_chart, 'XS', ('', 'XS', True)),
     (default_size_chart, '1XS', ('', 'XS', True)),
     (default_size_chart, '2XS', ('2', 'XS', True)),
     (default_size_chart, '15XS', ('15', 'XS', True)),
     (default_size_chart, 'XL', ('', 'XL', True)),
     (default_size_chart, '1XL', ('', 'XL', True)),
     (default_size_chart, '3XL', ('3', 'XL', True)),
     (default_size_chart, '10XL', ('10', 'XL', True)),
     (default_size_chart_and_dynamic_operations, 'M', ('', 'M', False)),
     (default_size_chart_and_dynamic_operations, 'XS', ('', 'XS', True)),
     (default_size_chart_and_dynamic_operations, '1XS', ('', 'XS', True)),
     (default_size_chart_and_dynamic_operations, '2XS', ('2', 'XS', True)),
     (default_size_chart_and_dynamic_operations, '15XS', ('15', 'XS', True)),
     (default_size_chart_and_dynamic_operations, 'XL', ('', 'XL', True)),
     (default_size_chart_and_dynamic_operations, '1XL', ('', 'XL', True)),
     (default_size_chart_and_dynamic_operations, '3XL', ('3', 'XL', True)),
     (default_size_chart_and_dynamic_operations, '10XL', ('10', 'XL', True)),
     (custom_size_chart, 'B', ('', 'B', False)),
     (custom_size_chart, 'A', ('', 'A', True)),
     (custom_size_chart, '1A', ('', 'A', True)),
     (custom_size_chart, '3A', ('3', 'A', True)),
     (custom_size_chart, '14A', ('14', 'A', True)),
     (custom_size_chart, 'C', ('', 'C', True)),
     (custom_size_chart, '1C', ('', 'C', True)),
     (custom_size_chart, '5C', ('5', 'C', True)),
     (custom_size_chart, '100C', ('100', 'C', True)),
    ],)
def test_parse_size_key(size_chart, size_key, expected_tpl):
    assert size_chart()._parse_size_key(size_key) == expected_tpl

    #TODO - Test Verbose and XXL keys    

@pytest.mark.parametrize("size_chart, size_key, expected_tpl", 
    [(default_size_chart, '-1XS', (ValueError, 'positive number or not set')),
     (default_size_chart, '+5XL', (ValueError, 'positive number or not set')),
     (default_size_chart_and_dynamic_operations, '-1XS', (ValueError, 'positive number or not set')),
     (default_size_chart_and_dynamic_operations, '+5XL', (ValueError, 'positive number or not set')),
     (custom_size_chart, '+2A', (ValueError, 'positive number or not set')),
     (custom_size_chart, '-5C', (ValueError, 'positive number or not set')),
    ],)
def test_parse_size_key_exception(size_chart, size_key, expected_tpl):
    
    with pytest.raises(expected_tpl[0]) as ee:
        size_chart()._parse_size_key(size_key)

    assert str(ee.value).find(expected_tpl[1]) > -1

    #TODO - Test Verbose and XXL keys    

def test_dynamic_size_cache(default_size_chart):
    chart_size = len(default_size_chart)
    default_size_chart.get_or_create_size('2XS')    #Size should remain the same
    assert chart_size == len(default_size_chart)   
    
    default_size_chart.enable_dynamic_size_cache()
    default_size_chart.get_or_create_size('2XL')   #Size should increase now
    chart_size += 1
    assert chart_size == len(default_size_chart) 

@pytest.mark.parametrize("size_chart, size_key, expected_tpl", 
    [(default_size_chart, 'XS', ('XS', 0, 'X-Small', True, ('2XS', 'S'))),
     (default_size_chart, '1XS', ('XS', 0, 'X-Small', True, ('2XS', 'S'))),
     (default_size_chart, '2XS', ('2XS', -10, '2X-Small', True, ('3XS', 'XS'))),
     (default_size_chart, '15XS', ('15XS', -140, '15X-Small', True, ('16XS', '14XS'))),
     (default_size_chart, 'XL', ('XL', 100, 'X-Large', True, ('L', '2XL'))),
     (default_size_chart, '1XL', ('XL', 100, 'X-Large', True, ('L', '2XL'))),
     (default_size_chart, '3XL', ('3XL', 120, '3X-Large', True, ('2XL', '4XL'))),
     (default_size_chart, '10XL', ('10XL', 190, '10X-Large', True, ('9XL', '11XL'))),
     (default_size_chart_and_dynamic_operations, 'XS', ('XS', 0, 'X-Small', True, ('2XS', 'S'))),
     (default_size_chart_and_dynamic_operations, '1XS', ('XS', 0, 'X-Small', True, ('2XS', 'S'))),
     (default_size_chart_and_dynamic_operations, '2XS', ('2XS', -10, '2X-Small', True, ('3XS', 'XS'))),
     (default_size_chart_and_dynamic_operations, '15XS', ('15XS', -140, '15X-Small', True, ('16XS', '14XS'))),
     (default_size_chart_and_dynamic_operations, 'XL', ('XL', 100, 'X-Large', True, ('L', '2XL'))),
     (default_size_chart_and_dynamic_operations, '1XL', ('XL', 100, 'X-Large', True, ('L', '2XL'))),
     (default_size_chart_and_dynamic_operations, '3XL', ('3XL', 120, '3X-Large', True, ('2XL', '4XL'))),
     (default_size_chart_and_dynamic_operations, '10XL', ('10XL', 190, '10X-Large', True, ('9XL', '11XL'))),
     (custom_size_chart, 'A', ('A', 1, 'A', True, ('2A', 'B'))),
     (custom_size_chart, '1A', ('A', 1, 'A', True, ('2A', 'B'))),
     (custom_size_chart, '3A', ('3A', -9, '3A', True, ('4A', '2A'))),
     (custom_size_chart, '14A', ('14A', -64, '14A', True, ('15A', '13A'))),
     (custom_size_chart, 'C', ('C', 3, 'C', True, ('B', '2C'))),
     (custom_size_chart, '1C', ('C', 3, 'C', True, ('B', '2C'))),
     (custom_size_chart, '5C', ('5C', 23, '5C', True, ('4C', '6C'))),
     (custom_size_chart, '100C', ('100C', 498, '100C', True, ('99C', '101C'))),
    ],)
def test_generate_dynamic_size(size_chart, size_key, expected_tpl):
    
    size_chart_gen = size_chart()._generate_dynamic_size(size_key)
    assert isinstance(size_chart_gen, Size)

    assert size_chart_gen.key == expected_tpl[0]
    assert size_chart_gen.sort_value == expected_tpl[1]
    assert size_chart_gen.verbose == expected_tpl[2]
    assert size_chart_gen.is_dynamic_size == expected_tpl[3]

    assert size_chart_gen.previous_size_key == expected_tpl[4][0]
    assert size_chart_gen.next_size_key == expected_tpl[4][1]

    #TODO - Test XXL keys    

@pytest.mark.parametrize("size_chart, size_key, expected_tpl",
    [(default_size_chart, '5M', (ValueError, 'Suffix is not defined as dynamic size')),
     (default_size_chart, 'B', (ValueError, 'Suffix is not defined as dynamic size')),
     (default_size_chart, '-5XS', (ValueError, 'positive number or not set')),
     (default_size_chart, '+4XL', (ValueError, 'positive number or not set')),
    ],)
def test_generate_dynamic_size_exception(size_chart, size_key, expected_tpl):
    with pytest.raises(expected_tpl[0]) as ee:
        default_size_chart()._generate_dynamic_size(size_key)

    assert str(ee.value).find(expected_tpl[1]) > -1

    #TODO - Test XXL keys    

@pytest.mark.parametrize("size_chart, size_key, expected_tpl", 
    [(default_size_chart, 'S', ('S', False, None, ('XS', 'M'))),
     (default_size_chart, 'M', ('M',  False, None, ('S', 'L'))),
     (default_size_chart, 'L', ('L',  False, None, ('M', 'XL'))),
     (default_size_chart, '2XL', ('XL', True, 1, ('XL', '3XL'))),
     (default_size_chart, '3XS', ('XS', True, -2, ('4XS', '2XS'))),
     (default_size_chart_and_dynamic_operations, 'S', ('S', False, None, ('XS', 'M'))),
     (default_size_chart_and_dynamic_operations, 'M', ('M', False, None, ('S', 'L'))),
     (default_size_chart_and_dynamic_operations, 'L', ('L', False, None, ('M', 'XL'))),
     (default_size_chart_and_dynamic_operations, '2XL', ('XL', True,  1, ('XL', '3XL'))),
     (default_size_chart_and_dynamic_operations, '3XS', ('XS', True, -2, ('4XS', '2XS'))),
    ],)
def test_size_key_to_size(size_chart, size_key, expected_tpl):
    
    dyn_size_base, _ = size_chart()._size_key_to_size(expected_tpl[0])
    assert dyn_size_base.key == expected_tpl[0]
    assert dyn_size_base.sort_value == SIZE_CHART_DEFAULTS[expected_tpl[0]].sort_value
    
    dyn_size, is_new = size_chart()._size_key_to_size(size_key)
    assert is_new == expected_tpl[1]
    assert (dyn_size.key not in size_chart().size_chart) == expected_tpl[1]
    if not is_new:
        return

    assert dyn_size.key == size_key
    factor = expected_tpl[2] * (DYNAMIC_OPERATION_DEFAULTS.smallest_increment
                                if dyn_size_base == DYNAMIC_OPERATION_DEFAULTS.key_smallest
                                else DYNAMIC_OPERATION_DEFAULTS.largest_increment)
    assert dyn_size.sort_value == SIZE_CHART_DEFAULTS[expected_tpl[0]].sort_value +factor       
    assert dyn_size.sort_value == dyn_size_base.sort_value + factor

    assert dyn_size.previous_size_key == expected_tpl[3][0]
    assert dyn_size.next_size_key == expected_tpl[3][1]

    #TODO - Test Verbose and XXL keys

@pytest.mark.parametrize("default_size_chart, size_key, expected_tpl",
    [(default_size_chart, '5M', (ValueError, 'Base size not')),
     (default_size_chart, 'B', (ValueError, 'Base size not')),
     (default_size_chart, '-5XS', (ValueError, 'positive number or not set')),
     (default_size_chart, '+4XL', (ValueError, 'positive number or not set')),
    ],)    
def test_test_size_key_to_size_exception(default_size_chart, size_key, expected_tpl):
    
    with pytest.raises(expected_tpl[0]) as ee:
        default_size_chart()._size_key_to_size(size_key)

    assert str(ee.value).find(expected_tpl[1]) > -1

@pytest.mark.parametrize("size_chart, size_key, expected_tpl", 
    [(default_size_chart, 'S', ('S', None, ('XS', 'M'))),
     (default_size_chart, 'M', ('M', None, ('S', 'L'))),
     (default_size_chart, 'L', ('L', None, ('M', 'XL'))),
     (default_size_chart, '2XL', ('XL', 1, ('XL', '3XL'))),
     (default_size_chart, '3XS', ('XS', -2, ('4XS', '2XS'))),
     (default_size_chart_and_dynamic_operations, 'S', ('S', None, ('XS', 'M'))),
     (default_size_chart_and_dynamic_operations, 'M', ('M', None, ('S', 'L'))),
     (default_size_chart_and_dynamic_operations, 'L', ('L', None, ('M', 'XL'))),
     (default_size_chart_and_dynamic_operations, '2XL', ('XL', 1, ('XL', '3XL'))),
     (default_size_chart_and_dynamic_operations, '3XS', ('XS', -2, ('4XS', '2XS'))),
    ],)
def test_get_or_create_size(size_chart, size_key, expected_tpl):
    
    dyn_size_base = size_chart().get_or_create_size(expected_tpl[0])
    assert dyn_size_base.key == expected_tpl[0]
    assert dyn_size_base.sort_value == SIZE_CHART_DEFAULTS[expected_tpl[0]].sort_value

    if size_key not in size_chart().size_chart:

        dyn_size = size_chart().get_or_create_size(size_key)
        assert dyn_size.key == size_key
        factor = expected_tpl[1] * (DYNAMIC_OPERATION_DEFAULTS.smallest_increment
                                    if dyn_size_base == DYNAMIC_OPERATION_DEFAULTS.key_smallest
                                    else DYNAMIC_OPERATION_DEFAULTS.largest_increment)
        assert dyn_size.sort_value == SIZE_CHART_DEFAULTS[expected_tpl[0]].sort_value +factor       
        assert dyn_size.sort_value == dyn_size_base.sort_value + factor

        assert dyn_size.previous_size_key == expected_tpl[2][0]
        assert dyn_size.next_size_key == expected_tpl[2][1]

    #TODO - Test Verbose and XXL keys

@pytest.mark.parametrize("default_size_chart, size_key, expected_tpl",
    [(default_size_chart, '5M', (ValueError, 'Base size not')),
     (default_size_chart, 'B', (ValueError, 'Base size not')),
     (default_size_chart, '-5XS', (ValueError, 'positive number or not set')),
     (default_size_chart, '+4XL', (ValueError, 'positive number or not set')),
    ],)    
def test_get_or_create_size_exception(default_size_chart, size_key, expected_tpl):
    
    with pytest.raises(expected_tpl[0]) as ee:
        default_size_chart().get_or_create_size(size_key)

    assert str(ee.value).find(expected_tpl[1]) > -1

@pytest.mark.parametrize("size_chart, list_length, expected_list", 
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
    ],)
def test_generate_lengthed_list(size_chart, list_length, expected_list):

    #Generate list is supposed to remove from left first for smaller, and add to right for larger
    assert size_chart().generate_lengthed_list(list_length) == expected_list

    #TODO - Test Verbose and XXL keys
    #TODO - Test Single-Ended

@pytest.mark.parametrize("size_chart, start_range, end_range, expected_list", 
    [(default_size_chart, 'M', 'M', ['M']),
     (default_size_chart, 'S', 'M', ['S','M']),
     (default_size_chart, 'XS', 'XL', ['XS','S','M','L','XL']),
     (default_size_chart, '2XS', 'XL', ['2XS','XS','S','M','L','XL']),
     (default_size_chart, 'M', '3XL', ['M','L','XL','2XL','3XL']),
     (default_size_chart, '2XS', '2XL', ['2XS','XS','S','M','L','XL','2XL']),
     (default_size_chart_and_dynamic_operations, 'S', 'S', ['S']),
     (default_size_chart_and_dynamic_operations, 'S', 'L', ['S','M','L']),
     (default_size_chart_and_dynamic_operations, 'XS', 'XL', ['XS','S','M','L','XL']),
     (default_size_chart_and_dynamic_operations, '2XS', 'XL', ['2XS','XS','S','M','L','XL']),
     (default_size_chart_and_dynamic_operations, 'S', '2XL', ['S','M','L','XL','2XL']),
     (default_size_chart_and_dynamic_operations, '2XS', '2XL', ['2XS','XS','S','M','L','XL','2XL']),
     (custom_size_chart, 'B', 'C', ['B','C']),
     (custom_size_chart, 'A', 'C', ['A','B','C']),
     (custom_size_chart, '3A', 'B', ['3A','2A','A','B']),
     (custom_size_chart, 'A', '4C', ['A','B','C','2C','3C','4C']),
     (custom_size_chart, '2A', '2C', ['2A','A','B','C','2C']),
    ],)
def test_generate_range(size_chart, start_range, end_range, expected_list):

    assert list(size_chart().generate_range_iter(start_range, end_range)) == expected_list
    assert size_chart().generate_range_list(start_range, end_range) == expected_list

    #TODO - Test Verbose and XXL keys
    #TODO - Test Single-Ended

@pytest.mark.parametrize("size_chart, start_range, end_range,  expected_tpl",
    [(default_size_chart, '5M', '5M', (ValueError, 'Base size not')),
     (default_size_chart, 'M', '5M', (ValueError, 'Base size not')),
     (default_size_chart, 'B', 'C', (ValueError, 'Base size not')),
     (default_size_chart, '-5XS', '-3XS', (ValueError, 'positive number or not set')),
     (default_size_chart, 'XS', '-3XS', (ValueError, 'positive number or not set')),
     (default_size_chart, '+4XL', '+7XL', (ValueError, 'positive number or not set')),
     (default_size_chart, 'XL', '+7XL', (ValueError, 'positive number or not set')),
    ],)
def test_generate_range_exception(size_chart, start_range, end_range, expected_tpl):

    with pytest.raises(expected_tpl[0]) as ee:
        list(size_chart().generate_range_iter(start_range, end_range))  #Need to invoke iter
    with pytest.raises(expected_tpl[0]) as ee:
        size_chart().generate_range_list(start_range, end_range)

    assert str(ee.value).find(expected_tpl[1]) > -1

if __name__ == "__main__":
    pytest.main(['-q', '-s', '--no-cov', 'tests/test_sizechart.py'])
