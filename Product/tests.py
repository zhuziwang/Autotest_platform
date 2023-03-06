from selenium import webdriver
# webdriver.Chrome()
import os
import requests
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Autotest_platform.settings')


class BasePageRequests:
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78'}


    def get(self, url, payload=None):
        """
        :param url: url（type:str）
        :param payload: params（type:dict）
        :return:
        """
        s = requests.get(url, params=payload, headers=self.headers)
        return s

    def post(self, url, payload_type=None, payload=None):
        """
        :param url: url（type:str）
        :param payload_type: data type（form:dict, json:str)
        :param payload: data
        :return:
        """
        if payload_type == 'dict':
            s = requests.post(url, data=payload, headers=self.headers)
            return s
        elif payload_type == 'str':
            s = requests.post(url, data=json.dumps(payload), headers=self.headers)
            return s


if __name__ == '__main__':
    a = BasePageRequests()
    a.get()
