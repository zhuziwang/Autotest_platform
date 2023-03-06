# -*- coding: utf-8 -*-
import re
import json
import requests
import logging
logger = logging.getLogger(__name__)
"""
str = 'aabbabaabbaa'

# 一个"."就是匹配除 \n (换行符)以外的任意一个字符
print(re.findall(r'a.b', str))  # ['aab', 'aab']

# *前面的字符出现0次或以上
print(re.findall(r'a*b', str))  # ['aab', 'b', 'ab', 'aab', 'b']

# 贪婪，匹配从.*前面为开始到后面为结束的所有内容
print(re.findall(r'a.*b', str))  # ['aabbabaabb']

# 非贪婪，遇到开始和结束就进行截取，因此截取多次符合的结果，中间没有字符也会被截取
print(re.findall(r'a.*?b', str))  # ['aab', 'ab', 'aab']

# 非贪婪，与上面一样，只是与上面的相比多了一个括号，只保留括号的内容
print(re.findall(r'a(.*?)b', str))  # ['a', '', 'a']
"""


class BasePage:
    seess = requests.session()
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.57',
               'charset': 'utf-8'}

    @staticmethod
    def send_all_request(**kwargs):
        res = BasePage.seess.request(**kwargs)
        return res

    def request_get(self, url,
                    params=None, cookies=None,
                    auth=None, timeout=None, allow_redirects=True, proxies=None,
                    stream=False, verify=False, cert=None):
        """
        :param url: 请求的url, type: str
        :param params: get请求的参数, type: dict. 例子: payload = {'key1': 'value1', 'key2': 'value2'},
                                                     payload = {'key1': 'value1', 'key2': ['value2', 'value3']}
        :param cookies: cookies type: dict
        :param auth: 身份认证，内网可能需要
        :param timeout: 连接，读取的超时时间, 可以是元组两个浮点数，也可以是一个整数，超过设置时间会报错
        :param allow_redirects: 请求重定向, 默认为: True
        :param proxies: 代理服务器, type: dict,
                        如果发送的是http请求，就使用http请求的代理，如果发送的是https请求，就使用一个https请求的代理。
                        proxies = {"https": "https://58.220.95.86:9401", "http": "http://113.214.13.1:1080"}
        :param stream: 原始响应内容
        :param verify: 默认会验证所访问网站证书，改为False为不验证所访问网站证书，访问网站为https时才会需要
        :param cert: SSL证书路径，如果verify设为文件夹路径，文件夹必须通过 OpenSSL 提供的 c_rehash 工具处理。
        :return:
        """
        cookies = json.loads(cookies)
        res = BasePage.send_all_request(method="get", url=url, params=params, headers=BasePage.headers, cookies=cookies,
                                        auth=auth, timeout=timeout, allow_redirects=allow_redirects, proxies=proxies,
                                        stream=stream, verify=verify, cert=cert)
        return res

    def request_post(self, url, content_type=None,
                     raw_type=None, data=None, cookies=None, files=None,
                     auth=None, timeout=None, proxies=None,
                     hooks=None, stream=None, verify=None, cert=None, json_json=None):
        """
        :param url:  请求的url, type: str
        :param content_type: 默认为None, 分别为: application/x-www-form-urlencoded: 浏览器的原生 form 表单 ,type: list, dict
                                               multipart/form-data: 上传文件用的表单 ,
                                               raw: 分为四种格式
                                               binary: 使用二进制流进行数据传输，多用于上传单个图片或图片。
                             用data参数提交数据时，request.body为a=1&b=2
                             用json参数提交数据时，request.body为'{"a": 1, "b": 2}'
        :param raw_type: raw的分类:  1.text/xml: xml格式文本,忽略xml头所指定编码格式而默认采用us-ascii编码 ,
                                    2.application/json: json格式文本,
                                    3.text/plain: 纯文本的形式，浏览器在获取到这种文件时并不会对其进行处理。
                                    4.application/xml: xml格式文本,会根据xml头指定的编码格式来编码,
                                    5.text/html: 浏览器在获取到这种文件时会自动调用html的解析器对文件进行相应的处理。
        :param data: type: dict.  如果不指定headers中content-type的类型，默认application/x-www-form-urlencoded
                                  使用data参数，报文是str类型，如果不指定headers中content-type的类型，默认application/json。
        :param cookies: cookies type: dict
        :param files:
        :param auth: 身份认证，内网可能需要
        :param timeout: 连接，读取的超时时间, 可以是元组两个浮点数，也可以是一个整数，超过设置时间会报错
        :param proxies: 代理服务器, type: dict,
                        如果发送的是http请求，就使用http请求的代理，如果发送的是https请求，就使用一个https请求的代理。
                        proxies = {"https": "https://58.220.95.86:9401", "http": "http://113.214.13.1:1080"}
        :param hooks:
        :param stream: 原始响应内容
        :param verify: 默认会验证所访问网站证书，改为False为不验证所访问网站证书，访问网站为https时才会需要
        :param cert: SSL证书路径，如果verify设为文件夹路径，文件夹必须通过 OpenSSL 提供的 c_rehash 工具处理。
        :param json_json: 用json参数提交数据时，request.body为'{"a": 1, "b": 2}'
                     不管报文是str类型，还是dict类型，如果不指定headers中content-type的类型，默认是：application/json。
        :return:
        """
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.57',
                   'charset': 'utf-8',
                   'content_type': 'data'}
        cookies = json.loads(cookies)
        if content_type == 'urlencoded':
            headers['content_type'] = 'application/x-www-form-urlencoded'
        elif content_type == 'data':
            headers['content_type'] = 'multipart/form-data'
        elif content_type == 'raw':
            if raw_type == 'text/xml':
                headers['content_type'] = 'text/xml'
            elif raw_type == 'application/json':
                headers['content_type'] = 'text/xml'
            elif raw_type == 'text/plain':
                headers['content_type'] = 'text/plain'
            elif raw_type == 'application/xml':
                headers['content_type'] = 'application/xml'
            elif raw_type == 'text/html':
                headers['content_type'] = 'text/html'
            else:
                return logger.error('没有该post传输类型')
        elif content_type == 'file':
            with open(files, 'rb') as data:
                headers['content_type'] = None
        else:
            return logger.error('没有该传输类型')
        res = BasePage.send_all_request(method="post", url=url, data=data, headers=headers, cookies=cookies,
                                        auth=auth, timeout=timeout, proxies=proxies, stream=stream,
                                        verify=verify, cert=cert, json=json_json)
        res.encoding = 'utf-8'
        return res

    def request_put(self, url,
                    params=None, data=None, headers=None, cookies=None, files=None,
                    auth=None, timeout=None, allow_redirects=True, proxies=None,
                    hooks=None, stream=None, verify=None, cert=None, json=None):
        res = BasePage.send_all_request(method="put")
        return res

    def request_delete(self, url,
                       params=None, data=None, headers=None, cookies=None, files=None,
                       auth=None, timeout=None, allow_redirects=True, proxies=None,
                       hooks=None, stream=None, verify=None, cert=None, json=None):
        res = BasePage.send_all_request(method="delete")
        return res

    def request_head(self, url,
                     params=None, data=None, headers=None, cookies=None, files=None,
                     auth=None, timeout=None, allow_redirects=True, proxies=None,
                     hooks=None, stream=None, verify=None, cert=None, json=None):
        res = BasePage.send_all_request(method="head")
        return res

    def request_options(self, url,
                        params=None, data=None, headers=None, cookies=None, files=None,
                        auth=None, timeout=None, allow_redirects=True, proxies=None,
                        hooks=None, stream=None, verify=None, cert=None, json=None):
        res = BasePage.send_all_request(method="options")
        return res


# if __name__ == '__main__':
#     a = BasePage()
#     b = a.request_post(url='http://www.baidu.com', content_type='urlencoded', data={}, verify=False)
#     print(b.text)
