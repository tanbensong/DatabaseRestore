from django.db import models
from django.contrib.auth.models import AbstractUser
from dbbash.base_model import BaseModel

# Create your models here.

class User(AbstractUser, BaseModel):
    '''用户模型类'''

    class Meta:
        db_table = 'db_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

# servername = models.ForeignKey("database.Server", on_delete=models.CASCADE, blank=True, null=True, verbose_name="可登录客户")
