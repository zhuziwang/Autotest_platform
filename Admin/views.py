# coding:utf-8
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
import json
import os
import pymysql
import time
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from django.views.decorators.csrf import csrf_exempt
from django.core import mail


# Create your views here.
def login(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)  # 认证给出的用户名和密码
        if user is not None and user.is_active:    # 判断用户名和密码是否有效
            auth.login(request, user)    # 保存会话状态
            request.session['user'] = username  # 跨请求的保持user参数
            response = HttpResponseRedirect('/admin/index')
            return response
        else:
            messages.add_message(request, messages.WARNING, '账户或者密码错误，请检查')
            return render(request, 'page/1登录.html')

    return render(request, 'page/1登录.html')


@login_required
def logout(request):
    auth.logout(request)
    return render(request, 'page/1登录.html')


@login_required
def index(request):
    return render(request, "page/首页.html")


# @csrf_exempt
@login_required
def project(request):
    return render(request, "page/2项目管理.html")


# @csrf_exempt
@login_required
def project_config(request, project_id):
    from Product.models import Project
    from Autotest_platform.helper.util import get_model
    p = get_model(Project, id=project_id)
    name = p.name if p else ""
    return render(request, "page/2项目管理--环境配置.html", {"projectId": project_id, "projectName": name})


# @csrf_exempt
@login_required
def page(request):
    return render(request, "page/3页面管理.html")


# @csrf_exempt
@login_required
def element(request):
    return render(request, "page/4页面元素.html")


# @csrf_exempt
@login_required
def keyword(request):
    return render(request, "page/5关键字库.html")


# @csrf_exempt
@login_required
def keyword_create(request):
    return render(request, "page/5-1新建关键字.html")


# @csrf_exempt
@login_required
def keyword_edit(request, keyword_id):
    from Product.models import Keyword, Project
    from Autotest_platform.helper.util import get_model
    kw = get_model(Keyword, id=keyword_id)
    projectId = kw.projectId if kw else 0
    p = get_model(Project, id=projectId)
    projectName = p.name if projectId > 0 and p else "通用"
    keywordName = kw.name if kw else ""
    return render(request, "page/5-2编辑关键字.html",
                  {"id": projectId, "projectName": projectName, "keywordId": keyword_id, "keywordName": keywordName})


# @csrf_exempt
@login_required
def testcase(request):
    return render(request, "page/6测试用例.html")


# @csrf_exempt
@login_required
def testcase_create(request):
    return render(request, "page/6-1新建测试用例.html")


# @csrf_exempt
@login_required
def testcase_edit(request, testcase_id):
    return render(request, "page/6-1编辑测试用例.html", {"testcaseId": testcase_id})


# @csrf_exempt
@login_required
def result(request):
    return render(request, "page/7测试结果.html")


# @csrf_exempt
@login_required
def result_see(request, result_id):
    return render(request, "page/7-1查看测试结果.html", {"id": result_id})


# @csrf_exempt
@login_required
def task(request):
    return render(request, "page/9任务管理.html")


# @csrf_exempt
@login_required
def loginConfig(request):
    return render(request, "page/8登录配置.html")


# @csrf_exempt
@login_required
def loginConfig_create(request):
    return render(request, "page/8-1新建登录配置.html")


# @csrf_exempt
@login_required
def loginConfig_edit(request, login_id):
    return render(request, "page/8-1编辑登录配置.html", {"id": login_id})


def e_email(subject, message, from_email, recipient_list):
    mail.send_mail(
        subject=str(subject),     # 题目
        message=str(message),     # 消息内容
        from_email=str(from_email),      # 发送者【当前配置邮箱】
        recipient_list=[recipient_list],      # 接收者邮箱
    )


def create_user():
    from django.contrib.auth.models import User
    # 创建普通用户
    User.objects.create_user(
        username='',
        password='',
        email=None,
    )


def create_supperuser():
    from django.contrib.auth.models import User
    # 创建超级用户
    User.objects.create_superuser(
        username='',
        password='',
        email='',
    )


def make_pwd(raw_pwd):
    from django.contrib.auth.hashers import make_password, check_password
    # 密码加密
    a = make_password(raw_pwd)
    # 验证密码
    return check_password(raw_pwd, a)


def set_pwd(username, raw_pwd, pwd):
    """
    :param username: 用户名
    :param raw_pwd: 原密码(明文)
    :param pwd: 新密码
    :return:
    """
    from django.contrib.auth.models import User
    user = User.objects.get(username=username)
    user_pwd = user.check_password(raw_pwd)
    if user_pwd:
        user.set_password(pwd)
        user.save()


def create_group(group_name):
    """
    创建组
    :param group_name: 组名
    :return:

    """
    from django.contrib.auth.models import Group
    group_obj = Group.objects.create(name=str(group_name))


def groups_permission(group_id, permission_id):
    """
    给组添加权限，相当于查找auth_group表和auth_permission表的id后，插入到auth_group_permission表一条/多条数据
    :param group_id: 组号（数据类型为Int）
    :param permission_id: 权限id（数据类型为：List）
    :return:
    """
    from django.contrib.auth.models import Permission, Group
    g_obj = Group.objects.filter(id=group_id)
    p_obj = Permission.objects.filter(id__in=permission_id)
    # *p: 把列表 p 的值依此传递到 g.permissions中
    g_obj.permissions.add(*p_obj)


def user_group(user_id, group_id):
    """
    给用户添加组的权限，相当于查找auth_user表和auth_group表的id后，插入到auth_user_groups表一条数据
    :param user_id: 用户id
    :param group_id: 组的id
    :return:
    """
    from django.contrib.auth.models import User, Group
    user_obj = User.objects.get(id=user_id)
    group_obj = Group.objects.get(group_id)
    user_obj.groups.add(group_obj)


def user_permissions(user_id, permissions_id):
    """
    给用户添加权限，相当于查找auth_user表和auth_permissions表的id后，插入到auth_user_user_permissions表一条/多条数据
    :param user_id: 用户id
    :param permissions_id: 权限id，（数据类型为：List）
    :return:
    """
    from django.contrib.auth.models import User, Group, Permission
    user_obj = User.objects.get(id=user_id)
    p_obj = Permission.objects.filter(id__in=permissions_id)
    user_obj.user_permissions.add(*p_obj)
