# SizeSorter
Simple module to sort an iterable by apparel size (...XS, S, M, L, XL...).
* Also includes utility functions to generate list of apparel sizes.
* Support for a mixture of numeric sizes, XXL / 2XL, etc.

**Time Complexity:** O(N Log N)  

**Space Complexity:** O(N) + O(SC) where SC is length of size chart
  
***

By all means, this module is overkill if you have a known or limited set of Sizes that you need
to support, such as ```['2XL', 'L', 'M', 'S', 'XL', 'XS']```.  

You can achieve this in 3-lines:

```python
array = ['2XL', 'L', 'M', 'S', 'XL', 'XS']
array_values = {'XS': 0, 'S': 25, 'M': 50, 'L': 75, 'XL': 100, '2XL': 140}
sorted_array = sorted(array, key=lambda x: array_values[x])
```

Where this module does become useful is when you don't control the sizes:
A new "X" size is added (ie: 4XS),
need to support say 'XXS'/ '2XL' or 'Small' / 'M' in same iterable,
and/or
have a mixture of sizes and numerics ('S', 4, 'M', 6).

## Usage

### How It Works


### Examples

todo

### Basic

todo

### Custom Size

todo

## Testing

todo
