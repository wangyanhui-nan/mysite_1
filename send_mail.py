# 在Django中发送邮件
# import os
# from django.core.mail import send_mail
#
# os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite_1.settings'
#
# if __name__ == '__main__':
#
#     send_mail(
#         '来自www.liujiangblog.com的测试邮件',
#         '欢迎访问www.liujiangblog.com，这里是刘江的博客和教程站点，本站专注于Python和Django技术的分享！',
#         'wyh2935333487@sina.com',
#         ['2935333487@qq.com'],
#     )

# 对于send_mail方法，第一个参数是邮件主题subject；第二个参数是邮件具体内容；第三个参数是邮件发送方，需要和你settings中的一致；
# 第四个参数是接受方的邮件地址列表。请按你自己实际情况修改发送方和接收方的邮箱地址。
#
# 另外，由于我们是单独运行send_mail.py文件，所以无法使用Django环境，需要通过os模块对环境变量进行设置，也就是：
#
# os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'


# 发送HTML格式的邮件
# 通常情况下，我们发送的邮件内容都是纯文本格式。但是很多情况下，我们需要发送带有HTML格式的内容，比如说超级链接。
# 一般情况下，为了安全考虑，很多邮件服务提供商都会禁止使用HTML内容，幸运的是对于以http和https开头的链接还是可以点击的。
import os
from django.core.mail import EmailMultiAlternatives

os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite_1.settings'

if __name__ == '__main__':

    subject, from_email, to = '来自www.liujiangblog.com的测试邮件', 'wyh2935333487@sina.com', '2935333487@qq.com'
    text_content = '欢迎访问www.liujiangblog.com，这里是刘江的博客和教程站点，专注于Python和Django技术的分享！'
    html_content = '<p>欢迎访问<a href="http://www.liujiangblog.com" target=blank>www.liujiangblog.com</a>，这里是刘江的博客和教程站点，专注于Python和Django技术的分享！</p>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()