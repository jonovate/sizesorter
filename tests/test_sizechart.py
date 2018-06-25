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
     DynOp,
     SizeChart,
     SIZE_CHART_DEFAULTS,
     DYNAMIC_OPERATIONS_DEFAULTS,
     SIZE_CHART_FORMAT_DEFAULTS
    )
from sizesorter.sizechart import SIZE_CHART_SIMPLE_EXAMPLE, SIZE_CHART_WOMENS_TOPS_EXAMPLE

# Doesn't work with Paramterized Test Cases. https://github.com/pytest-dev/pytest/issues/349
# @pytest.fixture(scope='module',
#                 params=[(SIZE_CHART_DEFAULTS, None),
#                         (SIZE_CHART_DEFAULTS, DYNAMIC_OPERATIONS_DEFAULTS)])
# def default_size_chart(request):
#     return SizeChart(*request.param)

@pytest.fixture(scope='module')
def default_size_chart():
    return SizeChart(SIZE_CHART_DEFAULTS, None)

@pytest.fixture(scope='module')
def default_size_chart_and_dynops():
    return SizeChart(SIZE_CHART_DEFAULTS, DYNAMIC_OPERATIONS_DEFAULTS)

def custom_dynops():
    return {'A': DynOp('A', 5, -1), 'C': DynOp('C', 5, 1)}

@pytest.fixture(scope='module')
def custom_size_chart():
    return SizeChart.from_simple_dict( {'A': 1, 'B': 2, 'C': 3}, custom_dynops())

@pytest.fixture(scope='module')
def baby_toddler_size_chart():
    
    #TODO - Test int and str keys
    baby_toddler_sizes = {
    'mo': Size('mo',0,'mo.',True),
    'T':  Size('T',25, 'T',True),
    '4': Size('4',54,'Size 4',False),
    '5': Size('5',55,'Size 5',False),
    '6': Size('6',56,'Size 6',False),
    '7': Size('7',57,'Size 7',False),
}
    #TODO -- Offset Increment
    #TODO - min/max dyn ops
    dyn_ops = {'mo': DynOp('mo',1,1), 'T': DynOp('T',1,1)}
    return SizeChart(baby_toddler_sizes, dyn_ops)

def test_class():
    size_chart = SizeChart()
    assert id(size_chart) > 0

    assert len(SIZE_CHART_DEFAULTS) == 5     # Make sure length hasn't changed ('XS' -> 'XL')
    assert len(size_chart) == len(SIZE_CHART_DEFAULTS)

    dyn_ops = {'XS': DynOp('XS', 1, -1), 'XL': DynOp('XL', 1, 1)}
    assert id(dyn_ops)

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
    [(1, (ValueError, 'of type Size')),
     (2, (ValueError, 'base suffix not in size_chart')),
     (3, (ValueError, 'base suffix not in size_chart')),
     (4, (ValueError, 'sort_value_increment must be a positive number')),
     (5, (ValueError, 'sort_value_increment must be a positive number')),
     (6, (ValueError, 'growth_direction must 1 or -1')),
     (7, (ValueError, 'growth_direction must 1 or -1')),
    ],)
def test_invalid_chart(test_case_id, expected_tpl):
    
    bad_size_chart = {'H': 4, 'J': Size('J', 10)}
    offset = {'A': DynOp('A', 25, -1), 'Z': DynOp('Z', 25, 1)}

    with pytest.raises(expected_tpl[0]) as ee:

        if test_case_id == 1:
            SizeChart(bad_size_chart)                           #Wrong Dict value
        
        del(bad_size_chart['H'])
        if test_case_id == 2:
            SizeChart(bad_size_chart, offset)               #Missing A

        bad_size_chart['A'] = Size('A', 1)
        if test_case_id == 3:            
            SizeChart(bad_size_chart, offset)               #Missing Z

        bad_size_chart['Z'] = Size('Z', 26)
        new_bad_offset = {'A': DynOp('A', 0, 1), 'Z': DynOp('Z', 0, -1)}        
        if test_case_id == 4:                      
            SizeChart(bad_size_chart, new_bad_offset)           #Bad increment

        new_bad_offset['A'] = DynOp('A', 50, 1)
        if test_case_id == 5:
            SizeChart(bad_size_chart, new_bad_offset)           #Bad increment

        new_bad_offset = {'A': DynOp('A', 50, -5), 'Z': DynOp('Z', 60, 4)}
        if test_case_id == 6:
            SizeChart(bad_size_chart, new_bad_offset)           #Bad growth

        new_bad_offset['A'] = DynOp('A', 50, -1)
        if test_case_id == 7:
            SizeChart(bad_size_chart, new_bad_offset)           #Bad growth

    assert str(ee.value).find(expected_tpl[1]) > -1

@pytest.mark.parametrize("test_case_id, expected_tpl", 
    [(1, (ValueError, 'Size Chart dictionary values must be Numbers')),
     (2, (ValueError, 'base suffix not in size_chart')),
     (3, (ValueError, 'base suffix not in size_chart')),
     (4, (ValueError, 'sort_value_increment must be a positive number')),
     (5, (ValueError, 'sort_value_increment must be a positive number')),
     (6, (ValueError, 'growth_direction must 1 or -1')),
     (7, (ValueError, 'growth_direction must 1 or -1')),
    ],)
def test_invalid_simple_chart(test_case_id, expected_tpl):
    
    bad_chart = {'J': 10, 'K': Size('K', 11)}
    offset = {'A': DynOp('A', 25, -1), 'Z': DynOp('Z', 25, 1)}

    with pytest.raises(expected_tpl[0]) as ee:
        
        if test_case_id == 1:
            SizeChart.from_simple_dict(bad_chart)                  #Wrong Dict Value
        
        del(bad_chart['K'])
        if test_case_id == 2:            
            SizeChart.from_simple_dict(bad_chart, offset)          #Missing A
                
        bad_chart['A'] = 1
        if test_case_id == 3:
            SizeChart.from_simple_dict(bad_chart, offset)           #Missing Z
        
        bad_chart['Z'] = 26
        new_bad_offset = {'A': DynOp('A', 0, -1), 'Z': DynOp('Z', 0, 1)}
        if test_case_id == 4: 
            SizeChart.from_simple_dict(bad_chart, new_bad_offset)           #Bad increment
        
        new_bad_offset = {'A': DynOp('A', 10, -1), 'Z': DynOp('Z', -5, 1)}
        if test_case_id == 5: 
            SizeChart.from_simple_dict(bad_chart, new_bad_offset)    #Bad increment

        new_bad_offset = {'A': DynOp('A', 10, -4), 'Z': DynOp('Z', 10, 4)}
        if test_case_id == 6: 
            SizeChart.from_simple_dict(bad_chart, new_bad_offset)           #Bad growth
        
        new_bad_offset['A'] = DynOp('A', 50, -1)
        if test_case_id == 7: 
            SizeChart.from_simple_dict(bad_chart, new_bad_offset)    #Bad growth

    assert str(ee.value).find(expected_tpl[1]) > -1

@pytest.mark.parametrize("size_chart, size_key, expected_tpl", 
    [(default_size_chart, 'M', (None)),
     (default_size_chart, 'XS', (DYNAMIC_OPERATIONS_DEFAULTS['XS'])),
     (default_size_chart, '1XS', (DYNAMIC_OPERATIONS_DEFAULTS['XS'])),
     (default_size_chart, '2XS', (DYNAMIC_OPERATIONS_DEFAULTS['XS'])),
     (default_size_chart, '-2XS', (DYNAMIC_OPERATIONS_DEFAULTS['XS'])),  #debatable
     (default_size_chart, '15XS', (DYNAMIC_OPERATIONS_DEFAULTS['XS'])),
     (default_size_chart, '1XL', (DYNAMIC_OPERATIONS_DEFAULTS['XL'])),
     (default_size_chart, 'XL', (DYNAMIC_OPERATIONS_DEFAULTS['XL'])),
     (default_size_chart, '3XL', (DYNAMIC_OPERATIONS_DEFAULTS['XL'])),
     (default_size_chart, '+3XL',(DYNAMIC_OPERATIONS_DEFAULTS['XL'])),  #debatable
     (default_size_chart, '10XL', (DYNAMIC_OPERATIONS_DEFAULTS['XL'])),
     (default_size_chart_and_dynops, 'M', (None)),
     (default_size_chart_and_dynops, 'XS', (DYNAMIC_OPERATIONS_DEFAULTS['XS'])),
     (default_size_chart_and_dynops, '1XS', (DYNAMIC_OPERATIONS_DEFAULTS['XS'])),
     (default_size_chart_and_dynops, '2XS', (DYNAMIC_OPERATIONS_DEFAULTS['XS'])),
     (default_size_chart_and_dynops, '-2XS', (DYNAMIC_OPERATIONS_DEFAULTS['XS'])),  #debatable
     (default_size_chart_and_dynops, '15XS', (DYNAMIC_OPERATIONS_DEFAULTS['XS'])),
     (default_size_chart_and_dynops, 'XL', (DYNAMIC_OPERATIONS_DEFAULTS['XL'])),
     (default_size_chart_and_dynops, '1XL', (DYNAMIC_OPERATIONS_DEFAULTS['XL'])),
     (default_size_chart_and_dynops, '3XL', (DYNAMIC_OPERATIONS_DEFAULTS['XL'])),
     (default_size_chart_and_dynops, '+3XL', (DYNAMIC_OPERATIONS_DEFAULTS['XL'])),  #debatable
     (default_size_chart_and_dynops, '10XL', (DYNAMIC_OPERATIONS_DEFAULTS['XL'])),
     (custom_size_chart, 'B', (None)),
     (custom_size_chart, 'A', (custom_dynops()['A'])),
     (custom_size_chart, '1A', (custom_dynops()['A'])),
     (custom_size_chart, '3A', (custom_dynops()['A'])),
     (custom_size_chart, '-3A', (custom_dynops()['A'])),  #debatable
     (custom_size_chart, '14A', (custom_dynops()['A'])),
     (custom_size_chart, '1C', (custom_dynops()['C'])),
     (custom_size_chart, 'C', (custom_dynops()['C'])),
     (custom_size_chart, '5C', (custom_dynops()['C'])),
     (custom_size_chart, '+5C', (custom_dynops()['C'])),  #debatable
     (custom_size_chart, '100C', (custom_dynops()['C'])),
    ],)
def test_find_dynamic_operation(size_chart, size_key, expected_tpl):
    assert size_chart()._find_dynamic_operation(size_key) == expected_tpl#[0]  #py collapses single

    #TODO - Test Verbose and XXL keys    

@pytest.mark.parametrize("size_chart, size_key, expected_tpl", 
    [(default_size_chart, 'M', ('M')),
     (default_size_chart, 'XL', ('XL')),
     (default_size_chart, '1XL', ('XL')),
     (default_size_chart, '10XL', ('10XL')),
     (default_size_chart, '11XL', ('11XL')),
     (default_size_chart, '1', ('1')),
     (default_size_chart, '10', ('10')),
     (default_size_chart, 1, ('1')),
     (default_size_chart, 10, ('10')),
    ],)
def test_handle_single_prefix(size_chart, size_key, expected_tpl):
    assert size_chart()._handle_single_prefix(size_key) == expected_tpl#[0] Single tpls unpack

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
     (default_size_chart_and_dynops, 'M', ('', 'M', False)),
     (default_size_chart_and_dynops, 'XS', ('', 'XS', True)),
     (default_size_chart_and_dynops, '1XS', ('', 'XS', True)),
     (default_size_chart_and_dynops, '2XS', ('2', 'XS', True)),
     (default_size_chart_and_dynops, '15XS', ('15', 'XS', True)),
     (default_size_chart_and_dynops, 'XL', ('', 'XL', True)),
     (default_size_chart_and_dynops, '1XL', ('', 'XL', True)),
     (default_size_chart_and_dynops, '3XL', ('3', 'XL', True)),
     (default_size_chart_and_dynops, '10XL', ('10', 'XL', True)),
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
     (default_size_chart_and_dynops, '-1XS', (ValueError, 'positive number or not set')),
     (default_size_chart_and_dynops, '+5XL', (ValueError, 'positive number or not set')),
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
     (default_size_chart_and_dynops, 'XS', ('XS', 0, 'X-Small', True, ('2XS', 'S'))),
     (default_size_chart_and_dynops, '1XS', ('XS', 0, 'X-Small', True, ('2XS', 'S'))),
     (default_size_chart_and_dynops, '2XS', ('2XS', -10, '2X-Small', True, ('3XS', 'XS'))),
     (default_size_chart_and_dynops, '15XS', ('15XS', -140, '15X-Small', True, ('16XS', '14XS'))),
     (default_size_chart_and_dynops, 'XL', ('XL', 100, 'X-Large', True, ('L', '2XL'))),
     (default_size_chart_and_dynops, '1XL', ('XL', 100, 'X-Large', True, ('L', '2XL'))),
     (default_size_chart_and_dynops, '3XL', ('3XL', 120, '3X-Large', True, ('2XL', '4XL'))),
     (default_size_chart_and_dynops, '10XL', ('10XL', 190, '10X-Large', True, ('9XL', '11XL'))),
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
    [(default_size_chart, '5M', (ValueError, 'Suffix is not defined as Dynamic Size')),
     (default_size_chart, 'B', (ValueError, 'Suffix is not defined as Dynamic Size')),
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
     (default_size_chart, '1XL', ('XL',  False, None, ('L', '2XL'))),
     (default_size_chart, '2XL', ('XL', True, 1, ('XL', '3XL'))),
     (default_size_chart, '3XS', ('XS', True, 2, ('4XS', '2XS'))),
     (default_size_chart_and_dynops, 'S', ('S', False, None, ('XS', 'M'))),
     (default_size_chart_and_dynops, 'M', ('M', False, None, ('S', 'L'))),
     (default_size_chart_and_dynops, 'L', ('L', False, None, ('M', 'XL'))),
     (default_size_chart_and_dynops, '2XL', ('XL', True,  1, ('XL', '3XL'))),
     (default_size_chart_and_dynops, '1XS', ('XS', False, 0, ('2XS', 'S'))),
     (default_size_chart_and_dynops, '3XS', ('XS', True, 2, ('4XS', '2XS'))),
    ],)
#expected_tpl = (dynamic key base key, is dynamic key, factor, (previous size key, next size key))
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
    exp_dyn_op = size_chart().dyn_ops[dyn_size_base.key]
    exp_factor = expected_tpl[2] * (exp_dyn_op.growth_direction * exp_dyn_op.sort_value_increment)
    assert dyn_size.sort_value == SIZE_CHART_DEFAULTS[expected_tpl[0]].sort_value + exp_factor
    assert dyn_size.sort_value == dyn_size_base.sort_value + exp_factor

    assert dyn_size.previous_size_key == expected_tpl[3][0]
    assert dyn_size.next_size_key == expected_tpl[3][1]

    #TODO - Test Verbose and XXL keys

@pytest.mark.parametrize("default_size_chart, size_key, expected_tpl",
    [(default_size_chart, '5M', (ValueError, 'Base size not')),
     (default_size_chart, 'B', (ValueError, 'Suffix is not defined as Dynamic')),
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
     (default_size_chart, '3XS', ('XS', 2, ('4XS', '2XS'))),
     (default_size_chart_and_dynops, 'S', ('S', None, ('XS', 'M'))),
     (default_size_chart_and_dynops, 'M', ('M', None, ('S', 'L'))),
     (default_size_chart_and_dynops, 'L', ('L', None, ('M', 'XL'))),
     (default_size_chart_and_dynops, '2XL', ('XL', 1, ('XL', '3XL'))),
     (default_size_chart_and_dynops, '3XS', ('XS', 2, ('4XS', '2XS'))),
    ],)
#expected_tpl = (dynamic key base key, factor, (previous size key, next size key))
def test_get_or_create_size(size_chart, size_key, expected_tpl):
    
    dyn_size_base = size_chart().get_or_create_size(expected_tpl[0])
    assert dyn_size_base.key == expected_tpl[0]
    assert dyn_size_base.sort_value == SIZE_CHART_DEFAULTS[expected_tpl[0]].sort_value

    if size_key not in size_chart().size_chart:

        dyn_size = size_chart().get_or_create_size(size_key)
        assert dyn_size.key == size_key

        assert dyn_size.key == size_key
        exp_dyn_op = size_chart().dyn_ops[dyn_size_base.key]
        exp_factor = expected_tpl[1] * (exp_dyn_op.growth_direction * exp_dyn_op.sort_value_increment)
        assert dyn_size.sort_value == SIZE_CHART_DEFAULTS[expected_tpl[0]].sort_value + exp_factor
        assert dyn_size.sort_value == dyn_size_base.sort_value + exp_factor

        assert dyn_size.previous_size_key == expected_tpl[2][0]
        assert dyn_size.next_size_key == expected_tpl[2][1]

    #TODO - Test Verbose and XXL keys

@pytest.mark.parametrize("default_size_chart, size_key, expected_tpl",
    [(default_size_chart, '5M', (ValueError, 'Base size not')),
     (default_size_chart, 'B', (ValueError, 'Suffix is not defined as Dynamic')),
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
     (default_size_chart_and_dynops, 1, ['M']),
     (default_size_chart_and_dynops, 2, ['M','L']),
     (default_size_chart_and_dynops, 3, ['S','M','L']),
     (default_size_chart_and_dynops, 5, ['XS','S','M','L','XL']),
     (default_size_chart_and_dynops, None, ['XS','S','M','L','XL']),
     (default_size_chart_and_dynops, 6, ['XS','S','M','L', 'XL','2XL']),
     (default_size_chart_and_dynops, 7, ['2XS','XS','S','M','L','XL','2XL']),
     (default_size_chart_and_dynops, 8, ['2XS','XS','S','M','L','XL','2XL','3XL']),
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
     (default_size_chart_and_dynops, 'S', 'S', ['S']),
     (default_size_chart_and_dynops, 'S', 'L', ['S','M','L']),
     (default_size_chart_and_dynops, 'XS', 'XL', ['XS','S','M','L','XL']),
     (default_size_chart_and_dynops, '2XS', 'XL', ['2XS','XS','S','M','L','XL']),
     (default_size_chart_and_dynops, 'S', '2XL', ['S','M','L','XL','2XL']),
     (default_size_chart_and_dynops, '2XS', '2XL', ['2XS','XS','S','M','L','XL','2XL']),
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
     (default_size_chart, 'M', '5M', (ValueError, 'Suffix is not defined as Dynamic')),
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
