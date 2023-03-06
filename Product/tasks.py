import json
import time

from celery.task import task


# 自定义要执行的task任务
@task(name='web/h5')
def SplitTask(result_id, result_type):
    """
    :param result_type: 判断是web/h5还是requests，暂时没用（0为web/h5，1为requests）
    :param result_id: 传过来的result表的Id
    :return: 判断result表result_id这条数据的environments字段是否符合条件，条件符合在splitresult表中插入一条数据
                并且实例化SplitTaskRunning方法，穿splitresult的id给SplitTaskRunning方法
             条件不符合也在splitresult表插入一条数据据，并且实例化SplitTaskRunning方法，穿splitresult的id给SplitTaskRunning方法

    """
    from Product.models import Result, SplitResult
    result = Result.objects.get(id=result_id)
    result.status = 20
    result.save()
    parameter = json.loads(result.parameter) if result.parameter else []
    browsers = json.loads(result.browsers) if result.environments else [1]
    environments = json.loads(result.environments) if result.environments else []
    for browser in browsers:
        # 判断有没有项目环境，如果有执行一下内容
        if environments:
            for environmentId in environments:
                # 判断测试用例的测试数据是否为True，如果为True执行如下内容，为False执行else（是否被参数化和用例断言）
                # 且当parameter中expect为空时（判断断言成功/失败），默认为True
                if parameter:
                    for params in parameter:
                        for k, v in params.items():
                            if v and isinstance(v, str):
                                if '#time#' in v:
                                    v = v.replace('#time#',
                                                  time.strftime('%Y%m%d', time.localtime(time.time())))
                                if '#random#' in v:
                                    import random
                                    v = v.replace('#random#', str(random.randint(1000, 9999)))
                                if '#null#' == v or '' == v:
                                    v = None
                                if '#logo#' == v:
                                    v = "/home/Atp/logo.png"
                                params[k] = v
                        # ensure_ascii 使用json.dumps写入一条中文数据需要参数ensure_ascii=False，否则中文数据为字符码
                        sr = SplitResult.objects.create(environmentId=environmentId, browserId=browser,
                                                        resultId=result.id,
                                                        parameter=json.dumps(params, ensure_ascii=False),
                                                        expect=params.get('expect', True))
                        SplitTaskRunning(sr.id)
                # 判断测试用例的测试数据,为False执行一下内容（parameter={}，是否被参数化和用例断言）,且当expect为空时默认expect=True
                else:
                    sr = SplitResult.objects.create(environmentId=environmentId, browserId=browser, resultId=result.id,
                                                    parameter={}, expect=True)
                    SplitTaskRunning(sr.id)
        # 判断项目环境，没有项目环境执行一下内容
        else:
            # 判断测试用例的测试数据，为True执行一下内容（是否被参数化和用例断言）
            if parameter:
                for params in parameter:
                    for k, v in params.items():
                        if v and isinstance(v, str):
                            if '#time#' in v:
                                v = v.replace('#time#', time.strftime('%Y%m%d', time.localtime(time.time())))
                            if '#random#' in v:
                                import random
                                v = v.replace('#random#', str(random.randint(1000, 9999)))
                            if '#null#' == v:
                                v = None
                            if '#logo#' == v:
                                v = "/home/Atp/logo.png"
                            params[k] = v
                    sr = SplitResult.objects.create(environmentId=0, browserId=browser, resultId=result.id,
                                                    parameter=json.dumps(params, ensure_ascii=False),
                                                    expect=params.get('expect', True))
                    SplitTaskRunning(sr.id)
            # 判断测试用例的测试数据，为False执行一下内容（是否被参数化和用例断言）
            else:
                sr = SplitResult.objects.create(environmentId=0, browserId=browser, resultId=result.id,
                                                parameter={}, expect=True)
                SplitTaskRunning(sr.id)
    SplitTaskRan(result_id)


def SplitTaskRan(result_id):
    """
    处理splitresult表和result表的status状态
    如果splitresult.result.id的数据中status都是30，result.status=30，否则result.status=40
    :param result_id:
    :return:
    """
    from Product.models import Result, SplitResult
    result = Result.objects.get(id=result_id)
    # 如果查找SplitResult表中有，条件为：resultId=result.id且status包含10或者20的数据，就休眠10秒，再继续向下执行
    while len(SplitResult.objects.filter(resultId=result.id, status__in=[10, 20])) > 0:
        time.sleep(10)
    # 获取SplitResult表中resultId字段对应的数据
    split_list = SplitResult.objects.filter(resultId=result.id)
    for split in split_list:
        # expect字段为1时，取出的值为True
        expect = split.expect
        # 如果split.status = 30，result_的值为True，否则为False
        result_ = True if split.status == 30 else False
        if expect != result_:
            result.status = 40
            result.save()
            return
    result.status = 30
    result.save()
    return


def SplitTaskRunning(splitResult_id):
    """
    运行用例
    :param splitResult_id: splitResult表的id
    :return:
    """
    from Product.models import SplitResult, Browser, Environment, Element, Check, Result, EnvironmentLogin, LoginConfig
    import django.utils.timezone as timezone
    from Autotest_platform.PageObject.Base import PageObject
    from Autotest_platform.helper.util import get_model
    split = SplitResult.objects.get(id=splitResult_id)
    result_ = Result.objects.get(id=split.resultId)
    steps = json.loads(result_.steps) if result_.steps else []
    parameter = json.loads(split.parameter) if split.parameter else {}
    checkType = result_.checkType
    checkValue = result_.checkValue
    checkText = result_.checkText
    selectText = result_.selectText
    beforeLogin = json.loads(result_.beforeLogin) if result_.beforeLogin else []
    split.status = 20
    split.save()
    split.startTime = timezone.now()
    environment = get_model(Environment, id=split.environmentId)
    host = environment.host if environment and environment.host else ''
    driver = None
    # 启动浏览器
    try:
        driver = Browser.objects.get(id=split.browserId).buid()
    except:
        split.status = 40
        split.remark = '浏览器初始化失败（启动失败）'
        split.finishTime = timezone.now()
        split.save()
        if driver:
            driver.quit()
        return
    # 判断Result表中的split.resultId字段关联的SplitResult表中的splitResult_id的 数据不为空且长度大于0
    # 判断是否有前置登陆
    if beforeLogin and len(beforeLogin) > 0:
        for bl in beforeLogin:
            login = get_model(LoginConfig, id=bl)
            # 断言类型
            loginCheckType = login.checkType
            # 断言值
            loginCheckValue = login.checkValue
            loginCheckText = login.checkText
            loginSelectText = login.selectText
            # 判断是否有在login表获取到数据
            # 如果没有获取到，执行一下内容
            if not login:
                split.loginStatus = 3
                split.status = 50
                split.remark = "找不到登陆配置,id=" + str(bl)
                split.finishTime = timezone.now()
                split.save()
                # 判断浏览器，如果已经打开浏览器，关闭浏览器
                if driver:
                    driver.quit()
                return
            # 在login表获取到数据
            loginSteps = json.loads(login.steps) if login.steps else []
            loginParameter = {}
            # 如果项目环境表不为空，获取前置登陆条件表对应的项目环境数据
            if environment:
                environmentLogin = get_model(EnvironmentLogin, loginId=bl, environmentId=environment.id)
                # 如果前置登陆条件对应项目环境数据正确，environmentLogin表对应的用例参数化数据
                if environmentLogin:
                    loginParameter = json.loads(environmentLogin.parameter) if environmentLogin.parameter else {}
            # 把从login表获取到的步骤循环
            for loginStep in loginSteps:
                try:
                    # 执行Step方法和该方法下的perform方法, loginParameter: 登陆前置条件的参数化
                    Step(loginStep.get("keywordId"), loginStep.get("values")).perform(driver, loginParameter, host)
                except Exception as e:
                    split.loginStatus = 2
                    split.status = 50
                    split.remark = "初始化登陆失败</br>登陆名称=" + str(login.name) + " , </br>错误信息=" + ("".join(e.args))
                    split.finishTime = timezone.now()
                    split.save()
                    if driver:
                        driver.quit()
                    return
            if loginCheckType:
                time.sleep(2)
                if loginCheckType == Check.TYPE_URL:
                    if not driver.current_url.endswith(str(loginCheckValue)):
                        split.loginStatus = 2
                        split.status = 50
                        split.remark = "初始化登陆失败</br>登陆名称=" + login.name + " , </br>错误信息=登录断言不通过"
                        split.finishTime = timezone.now()
                        split.save()
                        if driver:
                            driver.quit()
                        return
                elif loginCheckType == Check.TYPE_ELEMENT:
                    element = loginCheckValue
                    if str(loginCheckValue).isdigit():
                        element = get_model(Element, id=loginCheckValue)
                    try:
                        PageObject.find_element(driver, element)
                    except:
                        split.loginStatus = 2
                        split.status = 50
                        split.remark = "初始化登陆失败[ 登陆名称:" + login.name + " , 错误信息：断言不通过"
                        split.finishTime = timezone.now()
                        split.save()
                        if driver:
                            driver.quit()
                        return
        else:
            split.loginStatus = 1
    # 没有前置登陆
    index = 1
    for step in steps:
        try:
            Step(step.get("keywordId"), step.get("values")).perform(driver, parameter, host)
            index = index + 1
        except RuntimeError as re:
            split.status = 40
            split.remark = "测试用例执行第" + str(index) + "步失败，错误信息:" + str(re.args)
            split.finishTime = timezone.now()
            split.save()
            if driver:
                driver.quit()
            return
        except Exception as info:
            split.status = 40
            split.remark = "执行测试用例第" + str(index) + "步发生错误，请检查测试用例:" + str(info.args)
            split.finishTime = timezone.now()
            split.save()
            if driver:
                driver.quit()
            return
    remark = '测试用例未设置断言,建议设置'
    time.sleep(2)
    if checkType:
        if checkType == Check.TYPE_URL:
            TestResult = driver.current_url.endswith(checkValue)
            if not TestResult:
                if not split.expect:
                    remark = '测试通过'
                else:
                    remark = '测试不通过,预期结果为["' + checkValue + '"], 但实际结果为["' + driver.current_url + '"]'
            else:
                if split.expect:
                    remark = '测试通过'
                else:
                    remark = '测试不通过,预期结果为["' + checkValue + '"], 但实际结果为["' + driver.current_url + '"]'
        elif checkType == Check.TYPE_ELEMENT:
            element = checkValue
            expect_text = checkText
            select_text = selectText
            if str(checkValue).isdigit():
                element = get_model(Element, id=int(element))
            try:
                PageObject.find_element(driver, element)
                actual_text = PageObject.find_element(driver, element).text
                if select_text == 'all':
                    if expect_text == actual_text:
                        TestResult = True
                    else:
                        TestResult = False
                    if TestResult:
                        if split.expect:
                            remark = '测试通过，预期断言值完全匹配实际断言值。'
                        else:
                            remark = '测试不通过，预期结果失败，但实际结果是成功。'
                    else:
                        if not split.expect:
                            remark = '测试通过，预期结果失败，实际结果也是失败。'
                        else:
                            remark = '测试不通过，预期结果为["' + expect_text + '"]，但实际结果为["' + actual_text + '"]'
                else:
                    if expect_text in actual_text:
                        TestResult = True
                    else:
                        TestResult = False
                    if TestResult:
                        if split.expect:
                            remark = '测试通过，预期断言值包含匹配实际断言值。'
                        else:
                            remark = '测试不通过，预期结果失败，但实际结果是成功。'
                    else:
                        if not split.expect:
                            remark = '测试通过，预期结果失败，实际结果也是失败。'
                        else:
                            remark = '测试不通过，预期结果为["' + expect_text + '"]，但实际结果为["' + actual_text + '"]'
            except:
                TestResult = False
                remark = '当前元素定位已改变，请及时更新定位！'

    if driver:
        driver.quit()
    split.status = 30 if TestResult else 40
    split.remark = remark
    split.finishTime = timezone.now()
    split.save()
    return


def timingRunning():
    """
    定时任务执行的方法
    :return:
    """
    from Product.models import Task, TestCase, Result
    from Autotest_platform.helper.util import get_model
    tasks = Task.objects.filter(timing=1)
    for t in tasks:
        browsers = json.loads(t.browsers) if t.browsers else []
        testcases = json.loads(t.testcases) if t.testcases else []
        for tc in testcases:
            environments = tc.get("environments", [])
            tc = get_model(TestCase, id=tc.get("id", 0))
            r = Result.objects.create(projectId=tc.projectId, testcaseId=tc.id, checkValue=tc.checkValue,
                                      checkType=tc.checkType, checkText=tc.checkText, selectText=tc.selectText,
                                      title=tc.title, beforeLogin=tc.beforeLogin,
                                      steps=tc.steps, parameter=tc.parameter,
                                      browsers=json.dumps(browsers, ensure_ascii=False),
                                      environments=json.dumps(environments, ensure_ascii=False), taskId=t.id)
            SplitTask.apply_async(args=(r.id, 0), queue="web/h5")
            # SplitTask(r.id, 0)


class Step:
    def __init__(self, keyword_id, values):
        """
        :param keyword_id: 接收的login表下step字段下keyword_id，步骤的关键字id
        :param values: 接收的login表下step字段下，步骤的关键字的内容
        """
        from .models import Keyword, Params
        from Autotest_platform.helper.util import get_model
        self.keyword = get_model(Keyword, id=keyword_id)
        # 验证login表下的step子字段下的values的内容是否正确，返回值为一个obj列表
        self.params = [Params(value) for value in values]

    def perform(self, driver, parameter, host):
        """
        :param driver: 已启动的浏览器的driver
        :param parameter: 参数化内容
        :param host: 项目管理下项目的主机url
        :param login: login表obj
        :param split: split表obj
        :return:
        """
        from .models import Params, Element
        # 关键字类型是系统关键字
        if self.keyword.type == 1:
            values = list()
            # 把login表下的step字段的values步骤循环
            for p in self.params:
                # 测试用例步骤中使用了参数化
                if p.isParameter:
                    # 如果步骤中使用了参数化，且Type==element
                    if p.Type == Params.TYPE_ELEMENT:
                        # 获取Element表中id是：environmentlogin前置登陆表的parameter字段的p.value
                        # p.value：参数化的变量名，parameter.get：获取parameter字典的key
                        v = Element.objects.get(id=parameter.get(p.value, None))
                    # 步骤中使用了参数化，但是用例类型不是element
                    else:
                        v = parameter.get(p.value, None)
                # 测试用例步骤中没有使用参数化，但是用例类型是element
                elif p.Type == Params.TYPE_ELEMENT:
                    v = Element.objects.get(id=p.value)
                # 测试用例步骤中没有使用参数化，用例类型不是element
                else:
                    v = p.value
                # 关键字方法名是open_url且不包含:http://、https://
                if self.keyword.method == 'open_url' and not ('http://' in v or 'https://' in v):
                    v = 'http://' + host
                values.append(v)
            try:
                self.sys_method__run(driver, tuple(values))
            except:
                raise
        # 关键字类型是自定义关键字
        elif self.keyword.type == 2:
            steps = json.loads(self.keyword.steps)
            for pa in self.params:
                if not pa.isParameter:
                    if pa.Type == Params.TYPE_ELEMENT:
                        parameter[pa.key] = Element.objects.get(id=pa.value)
                    else:
                        parameter[pa.key] = pa.value
            for step in steps:
                try:
                    Step(step.get("keywordId"), step.get("values")).perform(driver, parameter, host)
                except:
                    raise

    def sys_method__run(self, driver, value):
        # 动态导入数据库中keyword表中，self回传对应的package字段值的文件路径和文件名
        package = __import__(self.keyword.package, fromlist=True)
        # 从动态导入的“package”文件下，获取keyword表中，self回传对应的clazz字段值的类名称，给clazz变量
        clazz = getattr(package, self.keyword.clazz)
        # 给clazz类下的drvier属性赋值 driver
        setattr(clazz, "driver", driver)
        # 从clazz类下，获取keyword表中，self回传对应的method字段值的方法名称，给mehtod变量
        method = getattr(clazz, self.keyword.method)

        def running(*args):
            try:
                c = clazz()
                para = (c,)
                args = para + args[0]
                method(*args)
            except:
                raise

        try:
            running(value)
        except:
            raise
