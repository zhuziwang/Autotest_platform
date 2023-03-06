def get_model(model, get=True, *args, **kwargs, ):
    """
    判断参数model是否是一个模型类的表，如果是返回该表下*args传参下的数据，如果不是提示model没有继承
    :param model: 表名
    :param get: 默认为True
    :param args: 传参2
    :param kwargs: 传参2
    :return:
    """
    from django.db.models.base import ModelBase
    # django中所有的model类都是ModelBase的子类
    # 判断传过来的model是不是一个表
    if isinstance(model, ModelBase):
        if get:
            try:
                return model.objects.get(*args, **kwargs)
            except:
                return None
        else:
            return model.objects.filter(*args, **kwargs)
    else:
        raise TypeError("model 没有继承 django.db.models.base.ModelBase")


def isLegal(string, length=5, match_='([^a-z0-9A-Z_])+'):
    import re
    pattern = re.compile(match_)
    match = pattern.findall(string)
    if string and len(string) > length:
        if match:
            return False
        else:
            return True
    else:
        return False


def md5(string):
    import hashlib
    return hashlib.md5(string.encode()).hexdigest()


def validateEmail(email):
    import re
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email):
            return True
    return False