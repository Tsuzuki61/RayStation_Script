MAPPING_ROOT_CLASS = '<root>'


class ObjectBuilder:
    def __init__(self, mapping):
        self.mapping = mapping

    def build(self, src):
        if isinstance(src, list):
            root_instance = self.build_sequence(src, self.mapping[MAPPING_ROOT_CLASS])
        else:
            root_instance = self.mapping[MAPPING_ROOT_CLASS]()
            self.build_object(root_instance, src)
        return root_instance

    def build_object(self, current, src):
        for key, value in src.items():
            if key in self.mapping:
                func = self.mapping[key]
                setattr(current, key, self.build_value(value, func))
            else:
                setattr(current, key, value)
        return current

    def build_sequence(self, src, func):
        current = []
        for value in src:
            current.append(self.build_value(value, func))
        return current

    def build_value(self, value, func):
        if isinstance(value, dict):
            result = self.build_object(func(), value)
        elif isinstance(value, list):
            result = self.build_sequence(value, func)
        else:
            result = func(value)
        return result


def ClassToJason_method(item):
    if isinstance(item, object) and hasattr(item, '__dict__'):
        return item.__dict__
    else:
        raise TypeError
