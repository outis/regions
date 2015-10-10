from collections import abc, OrderedDict

def strize(item):
    if hasattr(item, 'text'):
        return item.text
    return str(item)

class Row(abc.MutableMapping):
    @property
    def fields(self):
        return self._fields
    
    @fields.setter
    def fields(self, value):
        if not (hasattr(value, 'keys') and callable(value.keys)):
            value = [strize(tag).casefold() for tag in value]
        else:
            value = [s.casefold() for s in value]
        self._keys = value
        self._fields = OrderedDict.fromkeys(value)
    
    @property
    def keys(self):
        return self._keys
    
    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, value):
        if hasattr(value, 'name') and 'tr' == value.name:
            value = value('td', recursive=False)
        if self.stringify and hasattr(value[0], 'text'):
            value = [td.text.strip() for td in value]
        if value is not None:
            value += [None] * (len(self.keys) - len(value))
            value = OrderedDict((k, value[i]) for i, k in enumerate(self.keys))
        self._data = value
    
    def __init__(self, fields, data=None):
        self.default = None
        self.stringify = False
        self.fields = fields
        self.data = data
    
    def __contains__(self, key):
        return key in self.fields
    
    def __delitem__(self, key):
        if key in self.data:
            del self.data[key]
    
    def __eq__(self, other):
        for k in self.keys:
            if self.data[k] != other.data[k]:
                return False
        return True
    
    def __getitem__(self, key):
        if isinstance(key, str):
            key = key.casefold()
            if key in self._data:
                return self._data[key]
        elif hasattr(key, '__iter__'):
            return [self._data[k.casefold()] for k in key]
        elif isinstance(key, slice):
            return [self._data[k.casefold()] for k in self._keys[key]]
        if hasattr(self, 'default'):
            return self.default
        raise IndexError('No such key: ' + key)
    
    def __iter__(self):
        return self.keys.__iter__()
    
    def __len__(self):
        return len(self.keys)
    
    def __lt__(self, other):
        for k in self._keys:
            if self.data[k] > other.data[k]:
                return False
            if self.data[k] < other.data[k]:
                return True
        return False
    
    def __setitem__(self, key, value):
        if key in self.data:
            self.data[key] = value
    
    def __str__(self):
        return str(self.data)
    
    def addField(self, field):
        field = field.casefold()
        if field not in self._fields:
            self._fields[field] = field
            self._keys.append(field)
