# -*- coding: utf-8 -*-


def send_task_test(name, args=None, kwargs=None, countdown=None,
            eta=None, task_id=None, publisher=None, connection=None,
            result_cls=None, expires=None, queues=None, **options):
    """
    用于替代本地测试时send_task。

    Celery的send_task无视CELERY_ALWAYS_EAGER的存在。在本地测试时替换成此函数。

    """
    pos = name.rfind('.')
    module = name[:pos]
    func_name = name[pos + 1:]
    exec 'from %s import %s as func' % (module, func_name)
    if args and kwargs:
        result = func(*args, **kwargs)
    elif args:
        result = func(*args)
    elif kwargs:
        result = func(**kwargs)
    return result
