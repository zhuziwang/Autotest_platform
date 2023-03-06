"""Autotest_platform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.views.decorators.cache import cache_page
from django.contrib import admin
from django.conf.urls import url
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.views.static import serve
from django.conf import settings
from Admin.views import *
from Product.views import Project, Page, Element, Keyword, TestCase, TestResult, Public, TestTasks, Environment, Login#, \
    #User

urlpatterns = [
    # project    系统概括页面  项目名称
    path('api/v1/project/create', Project.create),
    path('api/v1/project/delete/<int:project_id>', Project.delete),
    path('api/v1/project/edit/<int:project_id>', Project.edit),
    path('api/v1/project', Project.find),
    path('api/v1/project/<int:project_id>', Project.get),
    # environment   项目管理页面
    path('api/v1/environment/create', Environment.create),
    path('api/v1/environment/delete/<int:environment_id>', Environment.delete),
    path('api/v1/environment/edit/<int:environment_id>', Environment.edit),
    path('api/v1/environment', Environment.find),
    path('api/v1/environment/<int:environment_id>', Environment.get),
    # page  页面管理页面
    path('api/v1/page/create', Page.create),
    path('api/v1/page/delete/<int:page_id>', Page.delete),
    path('api/v1/page/edit/<int:page_id>', Page.edit),
    path('api/v1/page', Page.find),
    path('api/v1/page/<int:page_id>', Page.get),
    # element   页面元素页面
    path('api/v1/element/create', Element.create),
    path('api/v1/element/delete/<int:element_id>', Element.delete),
    path('api/v1/element/edit/<int:element_id>', Element.edit),
    path('api/v1/element', Element.find),
    path('api/v1/element/<int:element_id>', Element.get),
    # keyword   关键字库页面
    path('api/v1/keyword/create', Keyword.create),
    path('api/v1/keyword/delete/<int:keyword_id>', Keyword.delete),
    path('api/v1/keyword/edit/<int:keyword_id>', Keyword.edit),
    path('api/v1/keyword', Keyword.find),
    path('api/v1/keyword/<int:keyword_id>', Keyword.get),
    path('api/v1/keyword/keywordpackage', Keyword.kwpackage),
    path('api/v1/keyword/keywordclazz', Keyword.kwpclazz_all),
    path('api/v1/keyword/keywordclazz/<int:package_id>', Keyword.kwpclazz),
    path('api/v1/keyword/keywordmethod', Keyword.kwpmethod_all),
    path('api/v1/keyword/keywordmethod/<int:clazz_id>', Keyword.kwpmethod),
    # testcase  测试用例页面
    path('api/v1/testcase/create', TestCase.create),
    path('api/v1/testcase/delete/<int:testcase_id>', TestCase.delete),
    path('api/v1/testcase/edit/<int:testcase_id>', TestCase.edit),
    path('api/v1/testcase', TestCase.find),
    path('api/v1/testcase/<int:testcase_id>', TestCase.get),
    path('api/v1/testcase/copy/<int:testcase_id>', TestCase.copy),

    path('api/v1/testcase/running/<int:testcase_id>', TestCase.test),       # 把测试用例发送给rabbit_mq
    # tasks     # 任务管理
    path('api/v1/task/create', TestTasks.create),
    path('api/v1/task/delete/<int:task_id>', TestTasks.delete),
    path('api/v1/task/edit/<int:task_id>', TestTasks.edit),
    path('api/v1/task', TestTasks.find),
    path('api/v1/task/<int:task_id>', TestTasks.get),
    path('api/v1/task/running/<int:task_id>', TestTasks.test),      # 运行任务，把任务（多条测试用例)发送给rabbit_mq
    # Login     # 登陆配置页面
    path('api/v1/login/create', Login.create),
    path('api/v1/login/delete/<int:login_id>', Login.delete),
    path('api/v1/login/edit/<int:login_id>', Login.edit),
    path('api/v1/login', Login.find),
    path('api/v1/login/<int:login_id>', Login.get),
    path('api/v1/login/bind/<int:login_id>', Login.bind),
    path('api/v1/login/unbind/<int:EnvironmentLogin_id>', Login.unbind),
    path('api/v1/login/bind/edit/<int:EnvironmentLogin_id>', Login.edit_bind),

    # result    测试结果页面
    path('api/v1/result', TestResult.find),
    path('api/v1/result/delete/<int:result_id>', TestResult.delete),
    path('api/v1/result/<int:result_id>', TestResult.get),

    # Public    公共接口
    path('api/v1/browser', Public.data),        # 返回browser表中id,name,value,remake字段的数据
    path('api/v1/projectSummary', Public.index),        # 系统概括页面--测试结果趋势统计数据
    path('api/v1/barChar', Public.bar_char),        # 系统概括页面--项目概括
    path('api/v1/lineChar', Public.line_char),      # 系统概括页面--测试结果趋势图

    path('index', cache_page(60)(index)),
    path('admin', admin.site.urls),
    path('admin/', admin.site.urls),
    path('login', login),   # 请求时登陆页，post请求时登陆接口
    path('login/', login),   # 请求时登陆页，post请求时登陆接口
    path('', index),   # 登陆页
    path('logout/', logout),     # 退出登陆
    path('admin/index', index),
    path('admin/project', project),
    path('admin/project/<int:project_id>', project_config),
    path('admin/page', page),
    path('admin/element', element),
    path('admin/keyword', keyword),
    path('admin/keyword/create', keyword_create),
    path('admin/keyword/edit/<int:keyword_id>', keyword_edit),
    path('admin/testcase', testcase),
    path('admin/testcase/create', testcase_create),
    path('admin/testcase/<int:testcase_id>', testcase_edit),    # 测试用例页面--编辑用例
    path('admin/loginConfig', loginConfig),
    path('admin/loginConfig/create', loginConfig_create),
    path('admin/loginConfig/edit/<int:login_id>', loginConfig_edit),    # 登陆配置项--编辑
    path('admin/task', task),
    path('admin/result', result),
    path('admin/result/<int:result_id>', result_see),       # 测试结果页面--查看测试结果用例

]

# 添加media路由
urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
