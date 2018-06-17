###
import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parentdir not in sys.path:
    sys.path.insert(0, parentdir)
###

import pytest
from sizesorter import SizeChart, x_offset, SIZE_CHART_DEFAULT
from sizesorter.sizechart import SIZE_CHART_WOMENS_TOPS_EXAMPLE

def test_class():
    size_chart = SizeChart()
    assert id(size_chart) > 0

    x_offsets = x_offset('XS', 1, 'XL', 1)
    assert id(x_offsets)

def test_invalid_chart():
    
    chart = {'J': 10}
    bad_offset = x_offset('A', 0, 'Z', -1)

    with pytest.raises(AssertionError) as err:
        SizeChart(chart, bad_offset)                  #Missing A
        chart['A'] = 1
        SizeChart(chart, bad_offset)                  #Missing Z

        chart['Z'] = 26
        SizeChart(chart, bad_offset)                  #Bad decrement
        SizeChart(chart, x_offset('A', 50, 'Z', -1))  #Bad increment

def test_generate_list():
    assert len(SIZE_CHART_DEFAULT) == 5     # Make sure length hasn't changed ('XS' -> 'XL')

    size_chart = SizeChart(SIZE_CHART_DEFAULT, None)

    list_1 = size_chart.generate_list(1)
    assert ['M'] == list_1

    list_2 = size_chart.generate_list(2)
    assert ['M', 'L'] == list_2

    list_3 = size_chart.generate_list(3)
    assert ['S', 'M', 'L'] == list_3

    list_5 = size_chart.generate_list(5)
    assert ['XS','S','M','L','XL'] == list_5

    list_6 = size_chart.generate_list(6)
    assert ['2XS','XS','S','M','L','XL'] == list_6

    list_7 = size_chart.generate_list(7)
    assert ['2XS','XS','S','M','L','XL','2XL'] == list_7

    list_8 = size_chart.generate_list(8)
    assert ['3XS','2XS','XS','S','M','L','XL','2XL'] == list_8

def test_generate_custom_list():
    custom_chart = {'A': 1, 'B': 2, 'C': 3}
    offset = x_offset('A', 5, 'C', 5)
    size_chart = SizeChart(custom_chart, offset)

    list_1 = size_chart.generate_list(1)
    assert ['B'] == list_1

    list_2 = size_chart.generate_list(2)
    assert ['B', 'C'] == list_2

    list_3 = size_chart.generate_list(3)
    assert ['A', 'B', 'C'] == list_3

    list_4 = size_chart.generate_list(4)
    assert ['2A', 'A', 'B', 'C'] == list_4

    list_7 = size_chart.generate_list(7)
    assert ['3A', '2A', 'A', 'B', 'C', '2C', '3C'] == list_7
