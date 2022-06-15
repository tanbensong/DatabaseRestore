from django.contrib import admin
from database.models import Server, DataName, Permissions
from user.models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class BaseAdmin(admin.ModelAdmin):
    list_per_page = 15
    actions_on_top = False
    actions_on_bottom = True


@admin.register(Server)
class ServerAdmin(BaseAdmin):
    list_display = ['name', 'address', 'loginmode', "servertype"]


@admin.register(DataName)
class ServerAdmin(BaseAdmin):
    list_display = ['server', 'name', 'database', 'port', 'password']
    list_filter = ['server']


@admin.register(Permissions)
class PermissionsAdmin(BaseAdmin):
    list_display = ['user']


admin.site.register(User, UserAdmin)
