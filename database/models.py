from django.db import models
from dbbash.base_model import BaseModel

# Create your models here.

class Server(BaseModel):
    """服务器模型类"""
    modes = (
        (0, "使用端口登陆"),
        (1, "使用密钥登陆"),
    )
    servertypes = (
        (0, "正式环境"),
        (1, "测试环境"),
    )

    name = models.CharField(max_length=128, unique=True, verbose_name="服务器名称")
    address = models.CharField(max_length=128, verbose_name="服务器地址")
    localhost = models.CharField(max_length=128, blank=True, null=True, verbose_name="内网地址")
    user = models.CharField(max_length=128, verbose_name="登录用户名")
    port = models.IntegerField(default=1022, verbose_name="登陆端口")
    password = models.CharField(max_length=128, blank=True, null=True, verbose_name="登陆密码")
    keyfile = models.FilePathField(path="/home/feidao/.ssh/", blank=True, null=True, verbose_name="密钥文件")
    loginmode = models.SmallIntegerField(default=0, choices=modes, verbose_name="登陆方式")
    servertype = models.SmallIntegerField(default=0, choices=servertypes, verbose_name="服务器类型")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "db_server"
        verbose_name = "服务器"
        verbose_name_plural = verbose_name


class Record(BaseModel):
    """操作记录模型类"""
    name = models.ForeignKey('DataName', on_delete=models.CASCADE, verbose_name="数据库名称")
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, verbose_name="还原用户")
    restore_time = models.DateTimeField(auto_now_add=False, verbose_name="还原时间")
    source = models.CharField(max_length=128, verbose_name="源数据库")
    target = models.CharField(max_length=128, verbose_name="目标数据库")

    class Meta:
        db_table = "db_record"
        verbose_name = "操作记录"
        verbose_name_plural = verbose_name


class DataName(BaseModel):
    """数据库模型类"""
    datanames = (
        (0, "SQL server"),
        (1, "MongoDB"),
        (2, "PostgreSQL"),
    )
    name = models.SmallIntegerField(default=0, choices=datanames, verbose_name="数据库名称")
    database = models.CharField(max_length=128, verbose_name="数据库名")
    server = models.ForeignKey('Server', on_delete=models.CASCADE, verbose_name="连接地址")
    user = models.CharField(max_length=128, verbose_name="连接用户")
    port = models.CharField(max_length=128, verbose_name="连接端口")
    password = models.CharField(max_length=128, verbose_name="用户密码")
    backuppath = models.CharField(max_length=128, default="/data/backup/file", verbose_name="备份目录")
    backupscripts = models.CharField(max_length=128, default="/data/backup", verbose_name="备份脚本")
    reductionscripts = models.CharField(max_length=128, default="/data/backup", verbose_name="还原脚本")

    def __str__(self):
        return "%s" % self.name
        # return self.name

    class Meta:
        db_table = "db_dataname"
        verbose_name = "数据库"
        verbose_name_plural = verbose_name


class Permissions(BaseModel):
    """用户权限模型类"""
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, verbose_name="关联用户")
    database = models.ManyToManyField('Server', verbose_name="关联客户")

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "db_permissions"
        verbose_name = "用户权限"
        verbose_name_plural = verbose_name
