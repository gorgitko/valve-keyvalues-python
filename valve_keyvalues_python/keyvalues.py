__author__ = "Jiri Novotny"
__version__ = "1.0.0"


# Source: https://github.com/gorgitko/valve-keyvalues-python


class KeyValues(dict):
    """
    Class for manipulation with Valve KeyValue (KV) files (VDF format). Parses the KV file to object with dict
    interface. 
    
    Allows to write objects with dict interface to KV files.
    """

    __re = __import__('re')
    __sys = __import__('sys')
    __codecs = __import__('codecs')
    __OrderedDict = __import__('collections').OrderedDict
    __regexs = {
        "key": __re.compile(r"""(['"])(?P<key>((?!\1).)*)\1(?!.)""", __re.I),
        "key_value": __re.compile(r"""(['"])(?P<key>((?!\1).)*)\1(\s+|)['"](?P<value>((?!\1).)*)\1""", __re.I)
    }

    def __init__(self, mapper=None, filename=None, encoding="utf-8", mapper_type=__OrderedDict, key_modifier=None,
                 key_sorter=None, ignore_bom=False):
        """
        :param mapper: initialize with own dict-like mapper
        :param filename: filename of KV file, which will be parsed to dict structure. Mapper param must not be specified
                         when using this param!
        :param encoding: KV file encoding. Default: 'utf-8'
        :param mapper_type: which mapper will be used for storing KV. It must have the dict interface, i.e. allow to do
                            the 'mapper[key] = value action'.
                            default: 'collections.OrderedDict'
                            For example you can use the 'dict' type.
        :param key_modifier: function for modifying the keys, e.g. the function 'string.lower' will make all the keys
                             lower
        :param key_sorter: function for sorting the keys when dumping/writing/str, e.g. using the function 'sorted'
                           will show KV keys in alphabetical order
        :param ignore_bom: Manual override flag to ignore the BOM marker at the start of the file and use the specified
                           encoding. Normal use should never see the user modifying this flag. Does nothing if filename
                           is not specified.
        """

        super().__init__()
        self.__sys.setrecursionlimit(100000)
        self.mapper_type = type(mapper) if mapper else mapper_type
        self.key_modifier = key_modifier
        self.key_sorter = key_sorter

        if not mapper and not filename:
            self.__mapper = mapper_type()
            return

        if mapper:
            self.__mapper = mapper
            return

        if isinstance(filename, str):
            self.parse(filename, encoding=encoding, ignore_bom=ignore_bom)
        else:
            raise Exception("'filename' argument must be string!")

    def __setitem__(self, key, item):
        self.__mapper[key] = item

    def __getitem__(self, key):
        return self.__mapper[key]

    def __repr__(self):
        # return repr(self.__mapper)
        return self.dump(self.__mapper)

    def __len__(self):
        return len(self.__mapper)

    def __delitem__(self, key):
        del self.__mapper[key]

    def clear(self):
        return self.__mapper.clear()

    def copy(self):
        """
        :return: mapper of KeyValues
        """
        return self.__mapper.copy()

    def has_key(self, k):
        return self.__mapper.has_key(k)

    # This function gets redef'd below and never used
    # def pop(self, k, d=None):
    #     return self.__mapper.pop(k, d)

    def update(self, *args, **kwargs):
        return self.__mapper.update(*args, **kwargs)

    def keys(self):
        return self.__mapper.keys()

    def values(self):
        return self.__mapper.values()

    def items(self):
        return self.__mapper.items()

    def pop(self, *args):
        return self.__mapper.pop(*args)

    def __cmp__(self, _dict):
        # cmp() does not exist in Py3, but we can just refer to the py3 dict __cmp__ implementation
        return super().__cmp__(self.__mapper, _dict)

    def __contains__(self, item):
        return item in self.__mapper

    def __iter__(self):
        return iter(self.__mapper)

    def __unicode__(self):
        # str is the idiomatic replacement for Py2's 'unicode()' function
        return str(repr(self.__mapper))

    def __str__(self):
        return self.dump()

    def __key_modifier(self, key, key_modifier):
        """
        Modifies the key string using the 'key_modifier' function.

        :param key:
        :param key_modifier:
        :return:
        """

        key_modifier = key_modifier or self.key_modifier

        if key_modifier:
            return key_modifier(key)
        else:
            return key

    def __parse(self, lines, mapper_type, i=0, key_modifier=None):
        """
        Recursively maps the KeyValues from list of file lines.

        :param lines:
        :param mapper_type:
        :param i:
        :param key_modifier:
        :return:
        """

        key = False
        _mapper = mapper_type()

        try:
            while i < len(lines):
                if lines[i].startswith("{"):
                    if not key:
                        raise Exception("'{{' found without key at line {}".format(i + 1))
                    _mapper[key], i = self.__parse(lines, i=i + 1, mapper_type=mapper_type, key_modifier=key_modifier)
                    continue
                elif lines[i].startswith("}"):
                    return _mapper, i + 1
                elif self.__re.match(self.__regexs["key"], lines[i]):
                    key = self.__key_modifier(self.__re.search(self.__regexs["key"], lines[i]).group("key"),
                                              key_modifier)
                    i += 1
                    continue
                elif self.__re.match(self.__regexs["key_value"], lines[i]):
                    groups = self.__re.search(self.__regexs["key_value"], lines[i])
                    _mapper[self.__key_modifier(groups.group("key"), key_modifier)] = groups.group("value")
                    i += 1
                elif self.__re.match(self.__regexs["key_value"], lines[i] + lines[i + 1]):
                    groups = self.__re.search(self.__regexs["key_value"], lines[i] + " " + lines[i + 1])
                    _mapper[self.__key_modifier(groups.group("key"), key_modifier)] = groups.group("value")
                    i += 1
                else:
                    i += 1
        except IndexError:
            pass

        return _mapper

    @staticmethod
    def _codec_detection(path, default) -> str:
        """
        Reads the front of a file to see if a [Byte Order Mark (BOM)](https://en.wikipedia.org/wiki/Byte_order_mark)
        exists. If so, it returns the codec that BOM usually corresponds to. A KV file with a BOM at the start that
        is improperly stripped will fail to detect the first Key line as the line doesn't start with '"' or an ASCII
        char.

        SOURCE: https://stackoverflow.com/a/24370596
        LICENSE: CC BY-SA 4.0
        AUTHOR: ivan_pozdeev

        :param path: The KV File path
        :param default: The default chosen encoding (usually UTF8)
        :return: A string of the encoding of the file (i.e. 'utf-8-sig', 'utf8', 'utf16', etc...)
        """
        with open(path, 'rb') as f:
            raw = f.read(4)  # will read less if the file is smaller
        # BOM_UTF32_LE's start is equal to BOM_UTF16_LE so need to try the former first
        for enc, boms in \
                ('utf-8-sig', (KeyValues.__codecs.BOM_UTF8,)), \
                ('utf-32', (KeyValues.__codecs.BOM_UTF32_LE, KeyValues.__codecs.BOM_UTF32_BE)), \
                ('utf-16', (KeyValues.__codecs.BOM_UTF16_LE, KeyValues.__codecs.BOM_UTF16_BE)):
            if any(raw.startswith(bom) for bom in boms):
                return enc
        return default

    def parse(self, filename, encoding="utf-8", mapper_type=__OrderedDict, key_modifier=None, ignore_bom=False):
        """
        Parses the KV file so this instance can be accessed by dict interface.

        :param filename: name of the KV file
        :param encoding: The encoding of the KV file. Default: 'utf-8'. Some KV files are UTF16-LE encoded.
        :param mapper_type: which mapper will be used for storing KV. It must have the dict interface,
                            i.e. allow to do the 'mapper[key] = value action'.
                            default: 'collections.OrderedDict'
                            For example you can use the 'dict' type. This will override the instance's 'mapper_type'
                            if specified during instantiation.
        :param key_modifier: function for modifying the keys, e.g. the function 'string.lower' will make all the keys
                            lower. This will override the instance's 'key_modifier' if specified during instantiation.
        :param ignore_bom: Manual override flag to ignore the BOM marker at the start of the file and use the specified
                           encoding. Normal use should never see the user modifying this flag.
        """
        _encoding = encoding
        _determined_codec = KeyValues._codec_detection(filename, _encoding)
        if _determined_codec != _encoding:
            print(f"Warning - The file codec was detected to be {_determined_codec.upper()} but {_encoding} was "
                  f"provided. Automatically using {_determined_codec.upper()} (pass ignore_bom=True to bypass this).")
            if not ignore_bom:
                _encoding = _determined_codec

        with open(filename, mode="r", encoding=_encoding) as f:
            lines = [line.strip() for line in f.readlines()]

        self.__mapper = self.__parse(lines,
                                     mapper_type=mapper_type or self.mapper_type,
                                     key_modifier=key_modifier or self.key_modifier)

    @staticmethod
    def __tab(string, level, quotes=False):
        if quotes:
            return '{}"{}"'.format(level * "\t", string)
        else:
            return '{}{}'.format(level * "\t", string)

    def __dump(self, mapper, key_sorter=None, level=0):
        string = ""

        if key_sorter:
            keys = key_sorter(mapper.keys())
        else:
            keys = mapper.keys()

        for key in keys:
            string += KeyValues.__tab(key, level, quotes=True)
            if isinstance(mapper[key], str):
                string += '\t "{}"\n'.format(mapper[key])
            else:
                string += "\n" + KeyValues.__tab("{\n", level)
                string += self.__dump(mapper[key], key_sorter=key_sorter, level=level + 1)
                string += KeyValues.__tab("}\n", level)

        return string

    def dump(self, mapper=None, key_sorter=None):
        """
        Dumps the KeyValues mapper to string.

        :param mapper: you can dump your own object with dict interface
        :param key_sorter: function for sorting the keys when dumping/writing/str, e.g. using the function 'sorted' will
                           show KV in alphabetical order. This will override the instance's 'key_sorter' if specified
                           during instantiation.
        :return: string
        """

        return self.__dump(mapper=mapper or self.__mapper, key_sorter=key_sorter or self.key_sorter)

    def write(self, filename, encoding="utf-8", mapper=None, key_sorter=None):
        """
        Writes the KeyValues to file.

        :param filename: output KV file name
        :param encoding: output KV file encoding. Default: 'utf-8'
        :param mapper: you can write your own object with dict interface
        :param key_sorter: key_sorter: function for sorting the keys when dumping/writing/str, e.g. using the function
                           'sorted' will show KV in alphabetical order.
                           This will override the instance's 'key_sorter' if specified during instantiation.
        """

        with open(filename, mode="w", encoding=encoding) as f:
            f.write(self.dump(mapper=mapper or self.__mapper, key_sorter=key_sorter or self.key_sorter))
