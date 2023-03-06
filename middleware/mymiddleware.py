import traceback
from django.core import mail
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class ExceptionMW(MiddlewareMixin):

    def process_exception(self, request, exception):

        print(exception)
        print(traceback.format_exc())

        # mail.send_mail(subject='报错了', message=traceback.format_exc(),
        #                from_email='2693601181@qq.com', recipient_list=settings.EX_EMAIL)

        return HttpResponse('---对不起，当前网页有点忙')
