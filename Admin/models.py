from django.db import models
# from django.contrib.auth.models import AbstractUser


# auth_user��
# is_staff�ֶ�Ϊ���жϸ��û��Ƿ���Ȩ�޵�½��վ��Ĺ���վ��
# is_activeΪ�����˺��Ƿ��ڻ״̬������Ƿǻ״̬��is_authenticated��has_perm()��has_perms()�Ȼ᷵��False


#
# class MyUserInfo(AbstractUser):
#     """
#     �̳�auth_user��ĸ���AbstractUser��ʵ����auth_user������ֶ�
#
#     ʹ���˼̳еķ�ʽ��Ҫʹ��authģ�飬��Ҫ��setting.py�н�������
#     Ĭ���û���֤ʱʹ�����ű�
#     AUTH_USER_MODEL = "Autotest_platform.MyUserInfo"
#     """
#     phone = models.IntegerField(max_length=11, blank=True)
#     addr = models.CharField(max_length=32, blank=True)
