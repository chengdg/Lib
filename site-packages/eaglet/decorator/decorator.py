# -*- coding: utf-8 -*-

class cached_context_property(object):
    """用于指定一个可以被context缓存的decorator

    ```
    @cached_context_property
    def name(self):
    	return 'hello ' + 'world'
    ```

    当我们调用`self.name`之后，`self.context['name'] = 'hello world'`，后续访问`self.name`，会直接从`self.context`中获取
    """
    def __init__(self, func):
        self.func = func
        self.func_name = func.__name__

    def __get__(self, instance, type=None):
        if instance is None:
            return self

        value = instance.context.get(self.func_name, None)
        if not value:
        	value = self.func(instance)
        	instance.context[self.func_name] = value
        return value


class ApiParamaterError(Exception):
    pass


def param_required(params=None):
    """用于检查函数参数的decorator

    ```
    @param_required(['id', 'name'])
    def name(self):
        return 'hello ' + 'world'
    ```
    """
    def wrapper(function):
        def inner(data):
            for param in params:
                if not param in data:
                    raise ApiParamaterError('Required parameter missing: %s' % param)
            return function(data)
        return inner 
    return wrapper