###
import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parentdir not in sys.path:
    sys.path.insert(0, parentdir)
###

from sizesorter import (
     Size,
     DynOp
    )

"""Minimal mapping of sizes to sort values"""
SIZE_CHART_SIMPLE = {
    'XS': 0,
    'S': 25,
    'M': 50,
    'L': 75,
    'XL': 100,
}

"""
Example mapping for Child sizes
Reference: https://www.carters.com/cs-sizing.html
"""
SIZE_CHART_BABY_TODDLER_KID_SIZES = {
    'P': Size('P',0,'Preemie',False),
    'NB': Size('NB',1,'Newborn',False),
    'M': Size('M',10,'mo.',True),   #3M 6M 9M 12M 18M 24M => 6
    'T': Size('T',100,'T',True),    #2T 3T 4T 5T => 4
    '4': Size('4',504,'Size 4',False),
    '5': Size('5',505,'Size 5',False),
    '6': Size('6',506,'Size 6',False),
    '7': Size('7',507,'Size 7',False),
}
DYNAMIC_OPS_BABY_TODDLER_KID_SIZES = {
    'M': DynOp('M',1,1),
    'T': DynOp('T',1,1),
}

"""
Example mapping for Women's Tops.
Used as an example to switch between say size 4-6 and S.
Reference: https://www.express.com/service/custserv.jsp?name=SizeChart
"""
SIZE_CHART_WOMENS_TOPS = {
    'XS': 0,
    'S': 4,
    'M': 8,
    'L': 12,
    'XL': 16,
}
