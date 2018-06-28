from django.db import models

# Create your models here.


class User(models.Model):
    gender = (
        ('male', '男'),
        ('female', '女'),
    )

    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    sex = models.CharField(max_length=32, choices=gender, default='男')
    c_time = models.DateTimeField(auto_now_add=True)
    # User模型新增了has_confirmed字段，这是个布尔值，默认为False，也就是未进行邮件注册；
    has_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        # 用于指定该模型生成的所有对象的排序方式，接收一个字段名组成的元组或列表。默认按升序排列，
        # 如果在字段名前加上字符“-”则表示按降序排列，如果使用字符问号“？”表示随机排列。
        ordering = ["-c_time"]
        verbose_name = "用户"    # 最常用的元数据之一！用于设置模型对象的直观、人类可读的名称。可以用中文。
        verbose_name_plural = "用户"  # 复数


class ConfirmString(models.Model):
    code = models.CharField(max_length=256)  # code字段是哈希后的注册码；
    user = models.OneToOneField('User', on_delete=models.CASCADE)    # user是关联的一对一用户；
    c_time = models.DateTimeField(auto_now_add=True)   # c_time是注册的提交时间。

    def __str__(self):
        return self.user.name + ":    " + self.code

    class Meta:
        ordering = ['-c_time']
        verbose_name = "确认码"
        verbose_name_plural = "确认码"
