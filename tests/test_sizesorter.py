###
import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)
###

import pytest
from sizesorter import SizeSorter

def test_class():
    ss = SizeSorter()
    assert id(ss) > 0
    
def test_numeric_to_x():
    
    with pytest.raises(AssertionError):
        SizeSorter._numeric_to_x(None)
        SizeSorter._numeric_to_x('3M')
        SizeSorter._numeric_to_x('XL')
    
    assert SizeSorter._numeric_to_x('1XL') == 'XL'
    assert SizeSorter._numeric_to_x('3XL') == 'XXXL'
    assert SizeSorter._numeric_to_x('1XS') == 'XS'
    assert SizeSorter._numeric_to_x('5XS') == 'XXXXXS'

def test_x_to_numeric():
    
    with pytest.raises(AssertionError):
        SizeSorter._x_to_numeric(None)
        SizeSorter._x_to_numeric('XXXM')
        SizeSorter._x_to_numeric('3XL')
    
    assert SizeSorter._x_to_numeric('XL') != '1XL'
    assert SizeSorter._x_to_numeric('XL') == 'XL'
    assert SizeSorter._x_to_numeric('XXXL') == '3XL'
    assert SizeSorter._x_to_numeric('XS') != '1XS'
    assert SizeSorter._x_to_numeric('XS') == 'XS'
    assert SizeSorter._x_to_numeric('XXXXXS') == '5XS'
