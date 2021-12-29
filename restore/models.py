from django.db import models

# Create your models here.

class ServerDatabase(models.Model):
    dataName = (
        (0, "MySQL"),
        (1, "SQL Server"),
        (2, "MongoDB"),
        (3, "PostgreSQL"),
    )

    name = models.SmallIntegerField(max_length=40, choices=dataName, verbose_name="数据库")
    post = models.IntegerField(validators=[], verbose_name="数据库端口")
    user = models.CharField(max_length=40, verbose_name="数据库用户")
    passwd = models.CharField(max_length=40, verbose_name="数据库密码")
    database = models.CharField(max_length=40, unique=True, verbose_name="数据库名称")
    remarks = models.CharField(max_length=20, null=True, blank=True, verbose_name="备注")

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = "tb_server_databases"
        verbose_name = "数据库信息"
        verbose_name_plural = verbose_name
