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

def test_class():
    size_chart = SizeChart()
    assert id(size_chart) > 0

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

def test_generate_list():
    assert len(SIZE_CHART_DEFAULTS) == 5     # Make sure length hasn't changed ('XS' -> 'XL')

    size_chart = SizeChart(SIZE_CHART_DEFAULTS, None)

    #Generate list is supposed to remove from left first for smaller, and add to right for larger
    list_1 = size_chart.generate_list(1)
    assert ['M'] == list_1

    list_2 = size_chart.generate_list(2)
    assert ['M', 'L'] == list_2

    list_3 = size_chart.generate_list(3)
    assert ['S', 'M', 'L'] == list_3

    list_5 = size_chart.generate_list(5)
    assert ['XS','S','M','L','XL'] == list_5

    list_6 = size_chart.generate_list(6)
    assert ['XS','S','M','L','XL', '2XL'] == list_6

    list_7 = size_chart.generate_list(7)
    assert ['2XS','XS','S','M','L','XL','2XL'] == list_7

    list_8 = size_chart.generate_list(8)
    assert ['2XS','XS','S','M','L','XL','2XL', '3XL'] == list_8

def test_generate_custom_list():
    custom_chart = {'A': 1, 'B': 2, 'C': 3}
    offset = dynamic_operation('A', 5, 'C', 5)
    size_chart = SizeChart.from_simple_dict(custom_chart, offset)

    #Generate list is supposed to remove from left first for smaller, and add to right for larger
    list_1 = size_chart.generate_list(1)
    assert ['B'] == list_1

    list_2 = size_chart.generate_list(2)
    assert ['B', 'C'] == list_2

    list_3 = size_chart.generate_list(3)
    assert ['A', 'B', 'C'] == list_3

    list_4 = size_chart.generate_list(4)
    assert ['A', 'B', 'C', '2C'] == list_4

    list_7 = size_chart.generate_list(7)
    assert ['3A', '2A', 'A', 'B', 'C', '2C', '3C'] == list_7
