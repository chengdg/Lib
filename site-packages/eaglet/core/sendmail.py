# -*- coding: utf-8 -*-

from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import smtplib
import settings


# todo 改回阿里邮箱
class MyMail(object):
    def __init__(self):
        self.account = settings.MAIL_NOTIFY_USERNAME
        self.password = settings.MAIL_NOTIFY_PASSWORD

    def send(self, dst_mail, title, content):
        date = datetime.now().strftime('%Y-%m-%d')
        msg = MIMEMultipart('alternative')
        msg['From'] = self.account
        msg['To'] = dst_mail
        msg['Subject'] = str(Header('%s' % title, 'utf-8'))
        c = MIMEText(content, _subtype='html', _charset='utf-8')
        msg.attach(c)
        server = smtplib.SMTP(settings.MAIL_NOTIFY_ACCOUNT_SMTP)
        # server = smtplib.SMTP_SSL(settings.MAIL_NOTIFY_ACCOUNT_SMTP)
        # server.docmd("EHLO server" )
        # server.starttls()
        server.login(self.account, self.password)
        server.sendmail(self.account, dst_mail.split(','), msg.as_string())
        server.close()


m = MyMail()


def sendmail(mail_address, title, content):
    m.send(mail_address, title, content)




# a1 = u'88787769@qq.com'
# a2 = u'\u5fae\u5546\u57ce-\u5f85\u652f\u4ed8-\u8ba2\u5355'
# a3 = u'\u5546\u54c1\u540d\u79f0\uff1a\u70ed\u5e72\u9762<br> \u8ba2\u5355\u53f7\uff1a20151224161321569<br> \u4e0b\u5355\u65f6\u95f4\uff1a2015-12-24 16:13<br> \u8ba2\u5355\u72b6\u6001\uff1a<font color="red">\u5f85\u652f\u4ed8</font><br> \u8ba2\u8d2d\u6570\u91cf\uff1a1<br> \u652f\u4ed8\u91d1\u989d\uff1a1.5<br> \u6536\u8d27\u4eba\uff1abill<br> \u6536\u8d27\u4eba\u7535\u8bdd\uff1a13811223344<br> \u6536\u8d27\u4eba\u5730\u5740\uff1a \u6cf0\u5174\u5927\u53a6'

# sendmail(u'88787769@qq.com,zhutianqi@weizoom.com',u'批量发送',u'222')

# sendmail(a1,a2,a3)
