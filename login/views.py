from django.shortcuts import render, redirect
from . import models
from . import forms
from django.conf import settings
import hashlib
import datetime
import pytz

# Create your views here.


# 1. 在顶部额外导入了redirect，用于logout后，页面重定向到‘index’首页；
# 2. 四个视图都返回一个render()调用，render方法接收request作为第一个参数，要渲染的页面为第二个参数，
#       以及需要传递给页面的数据字典作为第三个参数（可以为空），表示根据请求的部分，以渲染的HTML页面为主体，
#       使用模板语言将数据字典填入，然后返回给用户的浏览器。
# 3. 渲染的对象为login目录下的html文件，这是一种安全可靠的文件组织方式。
# 主页
def index(request):
    pass
    return render(request, 'login/index.html')

# HTMLform表单提交
# def login(request):
#     if request.method == "POST":
#         # 通过get('username', None)
#         # 的调用方法，确保当数据请求中没有username键时不会抛出异常，而是返回一个我们指定的默认值None；
#         username = request.POST.get('username', None)
#         password = request.POST.get('password', None)
#         message = "所有字段都必须填写！"
#         print(request.POST)
#         print(username, password)
#         if username and password:   # 确保用户名和密码都不为空
#             username = username.strip()  # 通过strip()方法，将用户名前后无效的空格剪除
#             password = password.strip()
#             # 用户名字符合法性验证
#             # 密码长度验证
#             # 更多的其它验证.....
#             try:
#                 user = models.User.objects.get(name=username)
#                 # 通过user.password == password进行密码比对，成功则跳转到index页面，失败则什么都不做。
#                 if user.password == password:
#                     return redirect('/index/')
#                 else:
#                     message = "密码不正确！"
#             except:
#                 message = "用户名不存在！"
#         return render(request, 'login/login.html', {'message': message})
#     return render(request, 'login/login.html')


# Django表单
# python代码生成HTML表单提交
# 对于非POST方法发送数据时，比如GET方法请求页面，返回空的表单，让用户可以填入数据；
# 对于POST方法，接收表单数据，并验证；
# 使用表单类自带的is_valid()方法一步完成数据验证工作；
# 验证成功后可以从表单对象的cleaned_data数据字典中获取表单的具体值；
# 如果验证不通过，则返回一个包含先前数据的表单给前端页面，方便用户修改。也就是说，它会帮你保留先前填写的数据内容，而不是返回一个空表！
# 登陆
def login(request):
    # 通过下面的if语句，我们不允许重复登录：
    if request.session.get('is_login', None):
        return redirect('/index/')

    if request.method == "POST":
        login_form = forms.UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = models.User.objects.get(name=username)
                if not user.has_confirmed:
                    message = '该用户还未通过邮件确认！'
                    return render(request, 'login/login.html', locals())
                if user.password == hash_code(password):
                    # 通过下面的语句，我们往session字典内写入用户状态和数据：
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name

                    return redirect('/index/')
                else:
                    message = "密码不正确！"
            except:
                message = "用户名不存在！"
        return render(request, 'login/login.html', locals())
    login_form = forms.UserForm()
    return render(request, 'login/login.html', locals())


# 注册
def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect('/index/')
    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        message = '请检查填写的内容！'
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            print(register_form.cleaned_data)
            if password1 != password2:
                message = '两次输入的密码不同！'
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                print(same_name_user)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'login/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:   # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'login/register.html', locals())

                # 当一切都OK的情况下，创建新用户
                new_user = models.User()
                new_user.name = username
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.sex = sex
                new_user.save()

                code = make_confirm_string(new_user)
                send_email(email, code)

                message = '请前往注册邮箱，进行邮箱确认！'
                return render(request, 'login/confirm.html', locals())

    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())


# 登出
def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect('/index/')
    # 删除当前的会话数据和会话cookie。经常用在用户退出后，删除会话。
    request.session.flush()
    return redirect('/index/')


# 密码加密
def hash_code(s, salt='mysite_1'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())   # update方法只接收bytes类型
    return h.hexdigest()


# make_confirm_string()是创建确认码对象的方法，代码如下：
def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name, now)
    models.ConfirmString.objects.create(code=code, user=user,)
    return code
# make_confirm_string()方法接收一个用户对象作为参数。首先利用datetime模块生成一个当前时间的字符串now，
# 再调用我们前面编写的hash_code()方法以用户名为基础，now为‘盐’，生成一个独一无二的哈希值，
# 再调用ConfirmString模型的create()方法，生成并保存一个确认码对象。最后返回这个哈希值。


# send_email(email, code)方法接收两个参数，分别是注册的邮箱和前面生成的哈希值，
def send_email(email, code):
    from django.core.mail import EmailMultiAlternatives
    subject = "来自www.liujiangblog.com的注册确认邮件"

    text_content = '''感谢注册www.liujiangblog.com，这里是刘江的博客和教程站点，专注于Python和Django技术的分享！\
                        如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'''

    html_content = '''
                        <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>www.liujiangblog.com</a>，\
                        这里是刘江的博客和教程站点，专注于Python和Django技术的分享！</p>
                        <p>请点击站点链接完成注册确认！</p>
                        <p>此链接有效期为{}天！</p>
                        '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
# 邮件内容中的所有字符串都可以根据你的实际情况进行修改。其中关键在于<a href=''>中链接地址的格式，
# 我这里使用了硬编码的'127.0.0.1:8000'，请酌情修改，url里的参数名为code，它保存了关键的注册确认码，
# 最后的有效期天数为设置在settings中的CONFIRM_DAYS。所有的这些都是可以定制的！


# 处理邮件确认请求
def user_confirm(request):
    code = request.GET.get('code', None)
    message = ''
    try:
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求！'
        return render(request, 'login/confirm.html', locals())

    c_time = confirm.c_time
    now = datetime.datetime.now()
    if now.replace(tzinfo=pytz.timezone('UTC')) > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '您的邮件已过期，请重新注册！'
        return render(request, 'login/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '感谢确认，请使用账户登陆'
        return render(request, 'login/confirm.html', locals())
# 说明：
#
# 通过request.GET.get('code', None)从请求的url地址中获取确认码;
# 先去数据库内查询是否有对应的确认码;
# 如果没有，返回confirm.html页面，并提示;
# 如果有，获取注册的时间c_time，加上设置的过期天数，这里是7天，然后与现在时间点进行对比；
# 如果时间已经超期，删除注册的用户，同时注册码也会一并删除，然后返回confirm.html页面，并提示;
# 如果未超期，修改用户的has_confirmed字段为True，并保存，表示通过确认了。然后删除注册码，但不删除用户本身。最后返回confirm.html页面，并提示。
