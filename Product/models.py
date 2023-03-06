import django.utils.timezone as timezone
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
import requests
import json
import random
import time


# Create your models here.
class Project(models.Model):
    """
    项目管理表
    name: 项目管理--项目名称
    remark: 项目管理--备注信息
    creator: 创建者
    createTime: 创建时间
    """
    name = models.CharField(max_length=20, null=False)
    remark = models.TextField(null=True)
    creator = models.CharField(max_length=20, null=False, default='admin')
    createTime = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'project'

    def clean(self):
        name = self.name.strip() if self.name else ""
        if 0 >= len(name) or len(name) > 20:
            raise ValidationError({'name': '无效的项目名称'})


class Page(models.Model):
    """
    页面管理--新建/编辑页面的表
    测试用例--新建测试用例--断言值
    """
    projectId = models.IntegerField()
    name = models.CharField(max_length=20, null=False)
    remark = models.TextField(null=True)
    createTime = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'page'

    def clean(self):
        name = self.name.strip() if self.name else ""
        projectId = int(self.projectId) if self.projectId and str(self.projectId).isdigit() else 0
        if 0 >= len(name) or len(name) > 20:
            raise ValidationError({'name': '无效的页面名称'})
        if projectId < 1:
            raise ValidationError({'projectId': '无效的项目Id'})


class Element(models.Model):
    """
    页面元素页面, 测试用例页面--新建测试用例--断言：选择断言页面page表后的元素
    projectId: 所属项目, 关联project表的id
    pageId: 所属页面, 关联page表的id
    name: 元素名称
    remark: 备注信息
    createTime: 创建时间
    """
    projectId = models.IntegerField()
    pageId = models.IntegerField()
    name = models.CharField(max_length=20, null=False)
    remark = models.TextField(null=True)
    createTime = models.DateTimeField(default=timezone.now)
    BY_TYPES = ["id", "xpath", "link text", "partial link text", "name", "tag name", "class name", "css selector"]
    by = models.CharField(null=False, max_length=20)
    locator = models.CharField(max_length=200, null=False)

    class Meta:
        db_table = 'element'

    def __str__(self):
        return self.name

    def clean(self):
        name = self.name.strip() if self.name else ""
        locator = str(self.locator) if self.locator else ""
        by = str(self.by).lower() if self.by else ""
        # projectId = int(self.projectId) if str(self.projectId).isdigit() else 0
        pageId = int(self.pageId) if str(self.pageId).isdigit() else 0
        if 0 >= len(name) or len(name) > 20:
            raise ValidationError({'name': '无效的元素名称'})
        # if projectId < 1:
        #     raise ValidationError({'projectId': 'projectId'})
        if pageId < 1:
            raise ValidationError({'pageId': '无效的页面Id'})
        if not by in Element.BY_TYPES:
            raise ValidationError({'by': 'by'})
        if 0 >= len(locator) or len(locator) > 200:
            raise ValidationError({'locator': '无效的定位值'})


class Keyword(models.Model):
    """
    关键字库表, 新建测试用例步骤的关键字
    projectId: 所属项目
    name: 关键字名称
    type: 关键字类型 （1：系统，2：自定义）
    package: 所属包，前台手动填写（需要使用的方法所在的位置） Autotest_platform.PageObject.Base
    clazz: 所属页面对象，前台手动填写（需要使用的方法所在的类） PageObject
    method: 需要使用的方法，前台手动填写
    params: 用例操作的步骤
    step: 步长（一组用例的用例条数）
    createTime: 创建时间
    remark: 备注信息
    """
    __KEYWORD_TYPES = {1: "system", 2: "custom"}
    projectId = models.IntegerField()
    name = models.CharField(max_length=20)
    type = models.IntegerField(default=2)
    package = models.CharField(max_length=200, null=True)
    clazz = models.CharField(max_length=50, null=True)
    method = models.CharField(max_length=50, null=True)
    params = models.TextField(null=True)
    steps = models.TextField(null=True)
    createTime = models.DateTimeField(default=timezone.now)
    remark = models.TextField(null=True)

    class Meta:
        db_table = "keyword"

    def clean(self):
        name = self.name.strip() if self.name else ""
        projectId = int(self.projectId) if str(self.projectId).isdigit() else 0
        package = self.package
        clazz = self.clazz
        method = self.method
        if not str(self.type).isdigit():
            raise ValidationError({'type': '无效的操作类型'})
        t = int(self.type)
        step = self.steps if self.steps else []
        if 0 >= len(name) or len(name) > 20:
            raise ValidationError({'name': '无效的关键字名称'})
        if projectId < 0:
            raise ValidationError({'projectId': '无效的项目Id'})
        if t == 1:
            try:
                obj = __import__(package, fromlist=[package.split(",")[-1]])
            except:
                raise ValidationError({'package': '无效的引用包'})
            try:
                obj = getattr(obj, clazz)
            except:
                raise ValidationError({'clazz': '无效的引用类'})
            try:
                getattr(obj, method)
            except:
                raise ValidationError({'method': '无效的引用方法'})
        elif t == 2:
            if isinstance(step, str):
                import json
                step = json.loads(step)
            if not isinstance(step, list):
                raise ValidationError({'step': '无效的操作步骤 : not list'})
            for s in step:
                if not isinstance(s, dict):
                    raise ValidationError({'step': '无效的操作步骤'})
                if not "keywordId" in s:
                    raise ValidationError({'step': '无效的操作步骤 : keywordId'})
                keywordId = int(s.get("keywordId")) if str(s.get("keywordId")).isdigit() else 0
                if keywordId < 1:
                    raise ValidationError({'step': '无效的操作步骤 : keywordId'})
                if not ("values" in s and isinstance(s.get("values"), list)):
                    raise ValidationError({'step': '无效的操作步骤 : values'})
                values = s.get("values")
                for value in values:
                    try:
                        Params(value)
                    except ValueError:
                        raise ValidationError({'step': '无效的操作步骤 : value'})
        else:
            raise ValidationError({'type': '无效的操作类型'})


class TestCase(models.Model):
    """
    用例表：存储所有用例
    projectId: 所属项目Id, 关联project表的id
    title: 用例标题
    level: 优先级
    beforeLogin: 前置登陆, login表的id
    steps: 步骤（isParameter:参数是否参数化）
    parameter: 测试用例的测试数据，包含参数换数据和预期结果判断是否正确（expect:预期结果是否正确）
    checkType: 断言类型, 1: "url", 2: "element"
    checkValue: 选择的断言的element表的Id
    checkText: 断言为元素，断言值的输入框
    selectText: 匹配类型（all：完全匹配， in：包含匹配）
    createTime: 创建时间
    remark: 备注信息
    """
    # TESTCASE_TYPES = {1: "功能测试", 2: "接口测试"}
    TESTCASE_STATUS = {1: "未执行", 2: "排队中", 3: "执行中"}
    TESTCASE_LEVEL = {1: "低", 2: "中", 3: "高", }
    TESTCASE_CHECK_TYPE = {1: "url", 2: "element"}
    projectId = models.IntegerField()
    title = models.CharField(max_length=200, null=False)
    # type = models.IntegerField(null=False, default=1)
    level = models.IntegerField(default=1)
    # status = models.IntegerField(null=False)
    beforeLogin = models.TextField(null=True)
    steps = models.TextField(null=False)
    parameter = models.TextField()
    checkType = models.TextField()
    checkValue = models.TextField()
    checkText = models.TextField(null=True)
    selectText = models.TextField(null=True)
    createTime = models.DateTimeField(default=timezone.now)
    remark = models.TextField(null=True)

    class Meta:
        db_table = "testcase"

    def clean(self):
        projectId = self.projectId if self.projectId else 0
        projectId = int(self.projectId) if str(projectId).isdigit() else 0
        title = self.title.strip() if self.title else ""
        # Type = self.type
        level = self.level
        # status = self.status
        step = self.steps
        parameter = self.parameter
        checkType = self.checkType
        checkValue = self.checkValue
        checkText = self.checkText
        selectText = self.selectText
        login = self.beforeLogin
        if not isinstance(login, list):
            raise ValidationError({'beforeLogin': '无效的登录配置'})
        if not projectId or projectId < 1:
            raise ValidationError({'projectId': '无效的项目Id'})
        if not title or 0 >= len(title) or len(title) > 200:
            raise ValidationError({'title': '无效的测试用例标题'})
        if not (level and level in TestCase.TESTCASE_LEVEL):
            raise ValidationError({'level': '无效的用例优先级'})
        # if not (status and status in TestCase.TESTCASE_STATUS):
        #     raise ValidationError({'level': 'Invalid level'})

        if not isinstance(step, list):
            raise ValidationError({'step': '无效的操作步骤 : steps'})
        for s in step:
            if not isinstance(s, dict):
                raise ValidationError({'step': '无效的操作步骤 : step'})
        #     if not "keywordId" in s:
        #         raise ValidationError({'step': '无效的操作步骤 1 : keywordId'})
        #     keywordId = int(s.get("keywordId")) if str(s.get("keywordId")).isdigit() else 0
        #     if keywordId < 1:
        #         raise ValidationError({'step': '无效的操作步骤 : keywordId'})
        #     if not ("values" in s and isinstance(s.get("values"), list)):
        #         raise ValidationError({'step': '无效的操作步骤 : values'})
        #     values = s.get("values")
        #     for value in values:
        #         try:
        #             Params(value)
        #         except ValueError:
        #             raise ValidationError({'step': '无效的操作步骤 : value '})
        if checkType:
            if checkValue:
                try:
                    Check(checkType, checkValue)
                except:
                    raise ValidationError({'check': '无效的断言'})
            else:
                raise ValidationError({'check': '无效的断言值'})
        if parameter:
            if isinstance(parameter, list):
                for p in parameter:
                    if 'expect' not in p:
                        raise ValidationError({'parameter': '测试数据中未找到预期结果'})
            else:
                raise ValidationError({'parameter': '无效的测试数据'})


class Environment(models.Model):
    """
    浏览器环境表（具体的项目和需要打开的地址表）
    projectId：project表的Id
    name：项目的名称
    host：访问的地址url
    remark：
    """
    projectId = models.IntegerField(null=True)
    name = models.CharField(max_length=20, null=False)
    host = models.TextField(null=False)
    remark = models.TextField(null=True)

    class Meta:
        db_table = 'Environment'

    def clean(self):
        """
        检查字符串projectId是否是只由大于0的数字组成，如果不是projectId=0
        如果projectId < 1 ,抛出异常提示
        如果name==None 或 name长度大于20或小于1，抛出异常提示
        如果host==None 或 host长度小于1，抛出异常提示
        :return:
        """
        projectId = int(self.projectId) if str(self.projectId).isdigit() and int(self.projectId) > 0 else 0
        name = self.name.strip() if self.name else ""
        host = self.host.strip() if self.host else ""
        if projectId < 1:
            raise ValidationError({'projectId': '无效的项目Id'})
        if not name or len(name) > 20 or len(name) < 1:
            raise ValidationError({'name': '无效的环境名称'})
        if not host or len(host) < 1:
            raise ValidationError({'host': '无效的环境域名'})


class Browser(models.Model):
    """
    浏览器表
    name:   浏览器名称
    value:  浏览器名称
    remark:
    installPath:    浏览器安装地址
    driverPath:     浏览器驱动地址
    """
    name = models.CharField(max_length=20, null=False)
    value = models.CharField(max_length=20, null=False)
    remark = models.TextField(null=True)
    installPath = models.TextField(null=True)
    driverPath = models.TextField(null=True)

    class Meta:
        db_table = 'Browser'

    def clean(self):
        """
        删除name字段值的前后空格，如果name长度<=0 或 name长度>20 ,抛出异常
        删除value字段值的前后空格，如果value长度<=0 或 name长度>20 ,抛出异常
        :return:
        """
        name = self.name.strip() if self.name else ""
        if 0 >= len(name) or len(name) > 20:
            raise ValidationError({'name': '无效的浏览器名称'})
        value = self.value.strip() if self.value else ""
        if 0 >= len(value) or len(value) > 20:
            raise ValidationError({'value': '无效的浏览器控制器'})

    def buid(self):
        """
        把browser字段值变为小写字母，并且删除前后空格
        判断browser字段的值，并启动对应的驱动
        :return:
        """
        browser = self.value.lower().strip() if self.value else ""
        if browser != 'android':
            from selenium import webdriver
            if browser == 'chrome':
                from selenium.webdriver.chrome.options import Options
                # options = Options()
                # chrome 59及之后的版本
                # 使用chrome（Chrome-headless）无头模式，教程地址：https://www.wunote.cn/article/2794/
                # options.add_argument('--headless')
                # 取消沙盒模式
                # options.add_argument('--no-sandbox')
                # options.add_argument('--disable-dev-shm-usage')
                # browser = webdriver.Chrome(chrome_options=options)
                browser = webdriver.Chrome()
            elif browser == 'firefox':
                browser = webdriver.Firefox()
            elif browser == 'edge':
                browser = webdriver.Edge()
            elif browser == 'ie':
                from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
                # 设置是否跳过保护模式检查，教程地址：https://www.pianshen.com/article/4357163799/
                DesiredCapabilities.INTERNETEXPLORER['ignoreProtectedModeSettings'] = True
                browser = webdriver.Ie()
            else:
                from selenium.webdriver.chrome.options import Options
                options = Options()
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                browser = webdriver.Chrome(chrome_options=options)
            browser.implicitly_wait(5)
            browser.maximize_window()
            return browser
        else:
            from appium import webdriver
            desired_caps = {

                'platformName': 'Android',

                'platformVersion': '9',

                'deviceName': '13b7cc66',   # 设别名称，随意

                'appPackage': 'com.android.browser',

                'appActivity': 'com.android.browser.BrowserActivity',

                'unicodeKeyboard': False,   # 使用自带输入法，输入中文时填True

                'resetKeyboard': True,  # 执行完程序恢复原来输入法

                "noReset": True,    # 不重置App

                "noSign": True,

                'newCommandTimeout': 6000,

                'antomationName': 'UiAutomator2'

            }
            import os
            all_apppackage = os.popen('adb shell pm list packages').read()
            app_package = 'com.android.browser'
            if app_package in all_apppackage:
                android_version = os.popen('adb shell getprop ro.build.version.release').read()
                desired_caps['platformVersion'] = android_version
                browser = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
                time.sleep(2)
                return browser
            else:
                print("没有该app：%s" % app_package)


class Result(models.Model):
    """
    发送出去执行的用例表，并返回执行结果的状态（用例结果首页 用例组/多条用例集合 的结果）
    title: 用例标题，testcase表的title
    taskId:
    projectId；project表的id
    testcaseId: testcase表的id
    browsers: 浏览器，来自browsers表，1：谷歌 2：火狐 3：手机
    beforeLogin: 前置登录，来自testcase表
    environments: 需要打开的网址，来自environments表
    status: 状态，10 排队中 20 测试中 30 成功  40 失败
    parameter: 测试数据
    steps: 步骤
    checkType: 断言类型, 1: "url", 2: "element"
    checkValue: 选择的断言的element表的Id
    checkText: 断言为元素，断言值的输入框
    createTime: 创建时间
    """
    title = models.CharField(max_length=200, null=False)
    taskId = models.IntegerField(null=True, default=0)
    projectId = models.IntegerField()
    testcaseId = models.IntegerField()
    browsers = models.TextField(null=True)
    beforeLogin = models.TextField(null=True)
    environments = models.TextField(null=True)
    status = models.IntegerField(default=10)  # 10 排队中 20 测试中 30 成功  40 失败
    parameter = models.TextField()
    steps = models.TextField(null=False)
    checkType = models.TextField()
    checkValue = models.TextField()
    checkText = models.TextField(null=True)
    selectText = models.TextField(null=True)
    createTime = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'Result'


class SplitResult(models.Model):
    """
    记录执行结果的表（用例结果组详情的结果）——（测试结果--结果详情）
    """
    environmentId = models.IntegerField(null=True)
    browserId = models.IntegerField(null=True)
    resultId = models.IntegerField()
    loginStatus = models.IntegerField(default=0)  # 1 成功  2 失败  3 跳过
    createTime = models.DateTimeField(default=timezone.now)
    startTime = models.DateTimeField(null=True)
    finishTime = models.DateTimeField(null=True)
    parameter = models.TextField()
    expect = models.BooleanField()
    status = models.IntegerField(default=10)  # 10 排队中 20 测试中 30 成功  40 失败 50跳过
    remark = models.TextField(null=True)
    

    class Meta:
        db_table = 'SplitResult'


class Task(models.Model):
    """
    任务管理页面
    name: 任务名称
    testcase: 测试用例（testcase表的Id）及环境（environmnet表的id）
    browsers:   选择的浏览器
    status:
    timing: 任务类型（1：定时任务，2：常规任务）
    remark: 备注信息
    createTime；创建时间
    """
    name = models.CharField(max_length=200, null=False)
    testcases = models.TextField(null=False)
    browsers = models.TextField(null=True)
    status = models.IntegerField(null=True, default=1)
    timing = models.IntegerField(null=False, default=1)  # 1 定时  2 常规
    remark = models.TextField(null=True)
    createTime = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'Task'

    def clean(self):
        name = self.name.strip() if self.name else ""
        testcases = self.testcases if self.testcases else []
        browsers = self.browsers if self.browsers else []
        if not name or len(name) > 20 or len(name) < 1:
            raise ValidationError({'name': '无效的任务名称'})
        if not (testcases and isinstance(testcases, list)):
            raise ValidationError({'testcases': '无效的测试用例集'})
        if not (browsers and isinstance(browsers, list)):
            raise ValidationError({'browsers': '无效的浏览器设置'})


class Params:
    """
    验证传过来的字典中的字段有没有 为空/false 的字段，并返回这个字典
    """
    TYPE_STRING = 'string'
    TYPE_ELEMENT = 'element'
    TYPE_FILE = 'file'
    TYPES = [TYPE_ELEMENT, TYPE_FILE, TYPE_STRING]

    def __init__(self, kwargs):
        """
        :param kwargs: 接收的字典
        获取kwargs的isParameter、type、key、value字段的值，并判断type字段的值是否是str类型，
        判断type字段的类型是否包含在Params.TYPES中，
        判断isParamter是否为空，且value是否为空或value去除空格后是否为空
        """
        isParameter = kwargs.get("isParameter", False)
        Type = kwargs.get("type", None)
        key = kwargs.get("key", None)
        value = kwargs.get("value", None)
        # str类型的Type必须有值
        if not (Type and isinstance(Type, str)):
            raise ValueError("Params object Type must be str type")
        Type = Type.lower()
        if Type not in Params.TYPES:
            raise ValueError("Params object Type value error")
        # 如果isParamter不为空，但是value为空或者value去除空格后为空
        if isParameter and (not value or str(value).strip() == 0):
            raise ValueError("Params Type parameter must has key")
        else:
            self.Type = Type
            self.key = key.strip()
            self.value = value
            self.isParameter = isParameter

    def __dict__(self):
        """
        :return: 以字典的形式返回__init__方法的字段值
        """
        obj = dict()
        obj["type"] = self.Type
        obj["isParameter"] = self.isParameter
        obj["value"] = self.value
        obj["key"] = self.key
        return obj


class Check:
    TYPE_URL = 'url'
    TYPE_ELEMENT = 'element'
    TYPES = [TYPE_URL, TYPE_ELEMENT]

    def __init__(self, type_, value):
        self.type = type_
        self.value = value
        if not (self.type and self.type in Check.TYPES):
            raise ValueError("Check对象的type属性值错误")
        if self.type and (value and not self.value.strip()):
            raise ValueError("Check对象的value属性不能为空")

    def __dict__(self):
        obj = dict()
        obj['type'] = self.type
        obj['value'] = self.value


class LoginConfig(models.Model):
    """
    登陆配置表
    projectId: project表的项目id
    name: 登陆名称
    remark: 备注信息
    checkType: 断言类型：url/element
    checkValue: 断言值的内容
    checkText:
    selectText: 匹配类型（all：完全匹配， in：包含匹配）
    steps: 步骤
    params:
    createTime: 创建时间
    """
    projectId = models.IntegerField()
    name = models.CharField(max_length=20, null=False)
    remark = models.TextField(null=True)
    checkType = models.TextField(default='')
    checkValue = models.TextField(default='')
    checkText = models.TextField(default='')
    selectText = models.TextField(default='')
    steps = models.TextField(null=False)
    params = models.TextField()
    createTime = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'login'

    def clean(self):
        name = self.name.strip() if self.name else ""
        step = self.steps
        checkType = self.checkType
        checkValue = self.checkValue
        checkText = self.checkText
        selectText = self.selectText
        if not name or 0 >= len(name) or len(name) > 20:
            raise ValidationError({'name': '无效的登录配置名称'})
        if not isinstance(step, list):
            raise ValidationError({'step': '无效的登录步骤 : steps'})
        for s in step:
            if not isinstance(s, dict):
                raise ValidationError({'step': '无效的登录步骤 : step'})
            if not "keywordId" in s:
                raise ValidationError({'step': '无效的登录步骤 : keywordId'})
            keywordId = int(s.get("keywordId")) if str(s.get("keywordId")).isdigit() else 0
            if keywordId < 1:
                raise ValidationError({'step': '无效的登录步骤 : keywordId'})
            if not ("values" in s and isinstance(s.get("values"), list)):
                raise ValidationError({'step': '无效的登录步骤 : values'})
            values = s.get("values")
            for value in values:
                try:
                    Params(value)
                except ValueError:
                    raise ValidationError({'step': '无效的登录步骤 : value'})
        try:
            Check(checkType, checkValue)
        except:
            raise ValidationError({'check': '无效的登录断言'})


class EnvironmentLogin(models.Model):
    """
    登陆配置页面-环境关联表
    loginid: login（登陆配置）表的id
    environmentId: envionment（项目需要打开的url，项目环境）表的id
    parameter: 参数化，参数
    """
    loginId = models.IntegerField()
    environmentId = models.IntegerField()
    parameter = models.TextField()

    class Meta:
        db_table = 'EnvironmentLogin'


class KeywordPackage(models.Model):
    """
    package: 所属包（需要使用的方法所在的位置） Autotest_platform.PageObject.Base
    remark: 备注信息
    """
    package = models.CharField(max_length=200, null=False)
    remark = models.TextField(null=True)

    class Meta:
        db_table = 'KeywordPackage'


class KeywordClazz(models.Model):
    """
    package: 所属包（KeywordPackage表id）
    clazz: 所属页面对象（需要使用的方法所在的类） PageObject
    remark: 备注信息
    """
    package = models.IntegerField(null=False)
    clazz = models.CharField(max_length=50, null=False)
    remark = models.TextField(null=True)

    class Meta:
        db_table = 'KeywordClazz'


class KeywordMethod(models.Model):
    """
    package: 所属包（KeywordPackage表id）
    clazz: 所属页面对象（KeywordClazz表id）
    method: 需要使用的方法
    remark: 备注信息
    """
    package = models.IntegerField(null=False)
    clazz = models.IntegerField(null=False)
    method = models.CharField(max_length=50, null=False)
    remark = models.TextField(null=True)

    class Meta:
        db_table = 'KeywordMethod'
