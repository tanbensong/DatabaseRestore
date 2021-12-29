from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class serverAddress(models.Model):
    statusSsh = (
        (0, "使用端口登陆"),
        (1, "使用密钥登陆")
    )

    server = models.CharField(max_length=20, unique=True, verbose_name="服务器地址")
    user = models.CharField(max_length=30, default="feidao", verbose_name="登陆用户")
    status = models.SmallIntegerField(default=0, choices=statusSsh, verbose_name="登陆方法")
    post = models.IntegerField(default=1022, verbose_name="远程端口")
    passwd = models.CharField(max_length=40, default="fdcf@2020", null=True, blank=True, verbose_name="用户密码")
    keyfile = models.FilePathField(path="/home/feidao/.ssh/", null=True, blank=True, verbose_name="密钥文件")

    def __str__(self):
        return str(self.server)

    class Meta:
        db_table = "tb_server_address"
        verbose_name = "服务器地址"
        verbose_name_plural = verbose_name


class programDevOps(models.Model):
    name = models.CharField(max_length=40, unique=True, verbose_name="程序名称")
    post = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(65535)], verbose_name="启动端口")
    start = models.CharField(max_length=100, verbose_name="启动命令")
    stop = models.CharField(max_length=100, verbose_name="停止命令")
    status = models.CharField(max_length=100, verbose_name="查看状态")

    def __str__(self):
        return str(self.name)
    
    class Meta:
        db_table = "tb_server_program"
        verbose_name = "服务器程序"
        verbose_name_plural = verbose_name
