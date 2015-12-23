# valve-keyvalues-python
Python class for manipulation with Valve KeyValues files ([VDF format](https://developer.valvesoftware.com/wiki/KeyValues)). Provides the parsing of VDF files to objects with dict interface, editing of this object keys and values and writing of any object with dict interface to VDF file.

# Installation
Just copy the `valve_keyvalues_python` folder or `keyvalues.py` file wherever you need, for example to your Python's site-packages: `<Python>/Lib/site-packages/` and then inside your program import the class by `from valve_keyvalues_python.keyvalues import KeyValues` or `from keyvalues import KeyValues`

**Requires Python 3!**

# Usage
### Instantiation

To create **empty** `KeyValues` instance:

```python
kv = KeyValues()
```

To create `KeyValues` instance **from VDF file**:

```python
kv = KeyValues(filename="")
```

Now you can access KeyValues with `dict` interface, i.e. with `kv[key] = value` operations.

When you create `KeyValues` instance from VDF file you can specify these optional parameters:

* `encoding=""` - input VDF file encoding. Default: `utf-8`
* `mapper_type=` - mapper type for storing KeyValues. It must have the `dict` interface, i.e. allow to do `mapper[key] = value` operations. For example you can use the `dict` type. **Instance's attribute**. Default: `collections.OrderedDict` (stores the keys in the order they have been added)
* `key_modifier=` - functions for modifying the key before its additions. For example `key_modifier=str.lower` will make all the keys to be lowercase. **Instance's attribute**. Default: `None`

To create `KeyValues` instance **from your own object with `dict` interface**:

```python
kv = KeyValues(mapper=)
```

Instance's attribute `mapper_type` will be set to type of passed `mapper=` object.

All these instantiation variants have common optional parameter `key_sorter=`. It's a sorting function which will be applied to keys when you use methods `dump()` or `write()` (or `print(kv)`, which is in fact shortcut for `print(kv.dump())`). For example you can use `key_sorter=sorted` and keys will be represented in alphabetical ascending order; `key_sorter=reversed` for reverse order. **Instance's attribute**. Default: `None`

### Methods
* `parse(filename)` - parses the VDF file to `dict` interface representation, i.e. KeyValues can be accessed and modified by `kv[key] = value` operations. Optional arguments:
  * `encoding=""` - input VDF file encoding. Default: `utf-8`
  * `mapper_type=` - [see Instantiation section](README.md#instantiation). This will override the instance's attribute `mapper_type`. Default: `collections.OrderedDict` (stores the keys in the order they have been added)
  * `key_modifier=` - [see Instantiation section](README.md#instantiation). This will override the instance's attribute `key_modifier`. Default: `None`
 
* `dump()` - returns the string representation of stored KeyValues, i.e. string in correct VDF format. Optional parameters:
  * `mapper=` - passed object will be dumped (it must have the `dict` interface!). Default: `None`
  * `key_sorter=` - [see Instantiation section](README.md#instantiation). This will override the instance's attribute `key_sorter`. Default: `None`

* `write(filename)` - writes the dump to file. Optional parameters:
  * `encoding=""` - output file encoding. Default: `utf-8`
  * `mapper=` - writes the dump of passed object (it must have the `dict` interface!). Default: `None`
  * `key_sorter=` - [see Instantiation section](README.md#instantiation). This will override the instance's attribute `key_sorter`. Default: `None`

Of course the class KeyValues also provides the standard `dict` interface methods like `keys()` or `key in d`. [See dict](https://docs.python.org/3.5/library/stdtypes.html#dict)

*Note*: when you `print(kv)` your KeyValues instance, it's in fact a shortcut for `print(kv.dump())` method (because magic method `__str__()` is defined that way).

# [Examples - here](examples/)

*example_01.py* - basic operations

*example_02.py* - using the optional functions

*example_03.py* - "advanced" uses

# What is missing

Generally the checking of VDF file syntax, i.e. if brackets are closed and so on. The only check is if after `"key"` is a starting bracket `{`.
