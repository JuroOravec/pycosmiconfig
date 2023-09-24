class imdict(dict):
    '''
    Simple immutable dict. Don't expect miracles.

    See https://stackoverflow.com/a/11026765/9788634
    '''

    def __hash__(self):
        return id(self)

    def _immutable(self, *args, **kws):
        raise TypeError("object is immutable")

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear = _immutable
    update = _immutable
    setdefault = _immutable
    pop = _immutable
    popitem = _immutable
