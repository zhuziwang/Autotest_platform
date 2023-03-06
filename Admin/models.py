from django.db import models
# from django.contrib.auth.models import AbstractUser


# auth_user表
# is_staff字段为：判断该用户是否有权限登陆该站点的管理站点
# is_active为：此账号是否处于活动状态，如果是非活动状态，is_authenticated、has_perm()、has_perms()等会返回False


#
# class MyUserInfo(AbstractUser):
#     """
#     继承auth_user表的父类AbstractUser，实现在auth_user表添加字段
#
#     使用了继承的方式，要使用auth模块，需要在setting.py中进行配置
#     默认用户认证时使用哪张表
#     AUTH_USER_MODEL = "Autotest_platform.MyUserInfo"
#     """
#     phone = models.IntegerField(max_length=11, blank=True)
#     addr = models.CharField(max_length=32, blank=True)
