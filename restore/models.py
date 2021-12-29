from django.db import models

# Create your models here.

class serverDatabase(models.Model):
    name = models.CharField(max_length=40, unique=True, verbose_name="数据库名称")
    post = models.IntegerField(validators=[], verbose_name="数据库端口")
    user = models.CharField(max_length=40, verbose_name="数据库用户")
    passwd = models.CharField(max_length=40, verbose_name="数据库密码")
    database = models.CharField(max_length=40, verbose_name="数据库名称")

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = "tb_server_databases"
        verbose_name = "服务器程序"
        verbose_name_plural = verbose_name
