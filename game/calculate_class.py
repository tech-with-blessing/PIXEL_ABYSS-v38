import sys

def get_total_size(obj, seen=None):
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    if hasattr(obj, '__dict__'):
        for k, v in obj.__dict__.items():
            size += get_total_size(v, seen)
    elif hasattr(obj, '__iter__'):
        if hasattr(obj, 'keys'):  # for dictionary
            for k in obj:
                size += get_total_size(obj[k], seen)
        elif not isinstance(obj, str):  # Other iterable, not string
            for item in obj:
                size += get_total_size(item, seen)
    return size

'''
class MyClass:
    def __init__(self):
        self.a = 1
        self.b = 2
        self.c = "hello"
        self.d = [1, 2, 3]

obj = MyClass()
print(get_total_size(obj))
'''