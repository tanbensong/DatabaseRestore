from unicodedata import name
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator

from database.models import Permissions, Server, DataName, Record
from user.models import User
from database.sshClient import SSHAgent
from datetime import datetime

# Create your views here.

class  homeViews(View):
    """首页"""
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:  # 用户已登陆
            username = request.user
            record =''
            if request.user.is_superuser:  # 超级管理员
                record = Record.objects.all().order_by("-id")
            else:
                user = User.objects.get(username=username)
                record = Record.objects.filter(user=user.id)
            # 分页
            paginator = Paginator(record, 25)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)

            num_pages = paginator.num_pages
            if num_pages < 9:
                page_range = range(1, num_pages+1)
            elif int(page_number) <= 5:
                page_range = range(1, 10)
            elif num_pages - int(page_number) <= 4:
                page_range = range(num_pages-8, num_pages+1)
            else:
                page_range = range(int(page_number)-4, int(page_number)+5)

            return render(request, self.template_name, locals())
        else:
            # 返回登陆界面        
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))


def databaseInfo(dbName):
    """数据库信息"""
    database = ''
    filename = ''
    targetFile = ''
    if dbName == "sqlserver":
        database = 0
        filename = 'pcb_biz.bak'
        targetFile = '/data/feidao/temp/mssql/'

    elif dbName == "mongodb":
        database = 1
        filename = 'pcb_erp_file'
        targetFile = '/data/feidao/temp/mongo/'
    elif dbName == "postgresql":
        database = 2
        filename = 'pcb_erp_clientmeta.out'
        targetFile = '/data/feidao/temp/pg/'

    return (database, filename, targetFile)


@login_required
def BackupDataViews(request):
    """数据库备份"""
    template_name = "backupdata.html"
    username = request.user

    if request.method == 'GET':
        try:
            server = Permissions.objects.get(user__username=username)
            servers = server.database.all()
        except:
            errmsg = "抱歉！您还没有任何可操作的服务器"
        
        return render(request, template_name, locals())

    if request.method == 'POST':
        dbname = request.POST.get('dataname').strip()
        database, filename, targetFile = databaseInfo(dbname)
        servername = request.POST.get('address').strip()
        server = Server.objects.get(name=servername)
        dataname = DataName.objects.filter(server=server.id).filter(name=database)[0]
        if server.loginmode == 0:
            client = SSHAgent(server.address, server.port, server.user, server.password)
        else:
            client = SSHAgent(server.address, server.port, server.user, pkeyfile=server.keyfile)
        stdin, stdout, stderr = client.runCommand("sudo sh {}".format(dataname.backupscripts))
        if stdout.channel.recv_exit_status() == 0:
            action = "备份成功"
        else:
            print(stdout.channel.recv_exit_status())
            print(stdout.read().decode('utf8'))
            action = "备份失败"
        information = {
            "address": servername,
            "dbname": dbname,
            "action": action,
        }

        return JsonResponse({"info": information})


@login_required
def ReductionViews(request):
    """数据库还原"""
    template_name = "database.html"
    username = request.user

    if request.method == 'GET':
        try:
            server = Permissions.objects.get(user__username=username)
            servers = server.database.all()
        except:
            errmsg = "抱歉！您还没有任何可操作的服务器"

        return render(request, template_name, locals())

    if request.method == 'POST':
        dbname = request.POST.get('dataname').strip()
        database, filename, targetFile = databaseInfo(dbname)

        sourceAddress = request.POST.get('sourceAddress').strip()
        targetAddress = request.POST.get('targetAddress').strip()
        dbname = request.POST.get('dataname').strip()
        dataPath = request.POST.get('dataPath').strip()
        ACTION = request.POST.get('action').strip()

        targetServer = Server.objects.get(name=targetAddress)
        sourceServer = Server.objects.get(name=sourceAddress)
        # 正式环境不参与还原
        if targetServer.servertype == 0:
            return JsonResponse({"info": "目标库为正式库，不支持在线还原！！"})
        else:
            # 发送文件
            if ACTION == "send":
                if sourceServer.loginmode == 0:
                    client = SSHAgent(
                        sourceServer.address,
                        sourceServer.port,
                        sourceServer.user,
                        sourceServer.password
                    )
                else:
                    client = SSHAgent(
                        sourceServer.address,
                        sourceServer.port,
                        sourceServer.user,
                        pkeyfile=sourceServer.keyfile
                    )
                dataname = DataName.objects.filter(server=sourceServer.id).filter(name=database)[0]
                datafile = dataname.backuppath + "/" + dataPath + "/" + filename
                chownCommand = "sudo chown {}:{} -R {}".format(
                    sourceServer.user,
                    sourceServer.user,
                    dataname.backuppath + "/" + dataPath
                )
                address = targetServer.localhost if targetServer.localhost else targetServer.address
                scpPort = 1022 if targetServer.localhost else targetServer.port
                client.runCommand(command=chownCommand)
                sendCommand = f"scp -r -P {scpPort} {datafile} {targetServer.user}@{address}:{targetFile + filename}"
                print(sendCommand)
                
                stdin, stdout, stderr = client.runCommand(sendCommand)
                if stdout.channel.recv_exit_status() != 0:
                    return JsonResponse({"info": "文件没有传输成功，请联系管理员！"})
                else:
                    return JsonResponse({"info": "文件传输完成"})
            else:
                if targetServer.loginmode == 0:
                    client = SSHAgent(
                        targetServer.address,
                        targetServer.port,
                        targetServer.user,
                        targetServer.password
                    )
                else:
                    client = SSHAgent(
                        targetServer.address,
                        targetServer.port,
                        targetServer.user,
                        pkeyfile=targetServer.keyfile
                    )
                client.runCommand(f"sudo rm -rf {targetFile + filename}.bak")
                dataname = DataName.objects.filter(server=targetServer.id).filter(name=database)[0]
                Command = f"""python3 {dataname.reductionscripts} -n {dbname} \
                    -p "{dataname.password}" -P {dataname.port} \
                    -u {dataname.user} -f {targetFile + filename} \
                    -D {dataname.database}
                """
                stdin, stdout, stderr = client.runCommand(Command)
                if stdout.channel.recv_exit_status() != 0:
                    client.runCommand(f"sudo mv {targetFile + filename} {targetFile + filename}.bak")
                    return JsonResponse({"info": "数据库还原失败，请联系管理员！"})
                else:
                    restoretime = datetime.strptime(dataPath.split('_')[1], "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
                    client.runCommand(f"sudo mv {targetFile + filename} {targetFile + filename}.bak")
                    # 保存还原记录
                    record = Record()
                    record.name = dataname
                    record.user = username
                    record.restore_time = restoretime
                    record.source = sourceAddress
                    record.target = targetAddress
                    record.save()
                    
                    information = {
                        "sourceAddress": sourceAddress,
                        "targetAddress": targetAddress,
                        "action": "还原成功",
                    }
                    return JsonResponse({"info": information})


def Dataname(request, server):
    """用户关联的数据库"""
    if not request.user.is_authenticated:
        raise PermissionDenied
    elif "HTTP_REFERER" not in request.META:
        raise PermissionDenied
    elif settings.REFERER[0] in request.META['HTTP_REFERER']  or settings.REFERER[1] in request.META['HTTP_REFERER']:
        server = Server.objects.get(name=server)
        datanames = DataName.objects.filter(server=server.id)
        datalists = []
        for data in datanames:
            datalist = ''
            if data.name == 0:
                datalist = ["SQL server", "sqlserver", "ERP 数据"]
            elif data.name == 1:
                datalist = ["MongoDB", "mongodb", "ERP 文件"]
            elif data.name == 2:
                datalist = ["PostgreSQL", "postgresql", "ERP 用户"]
            datalists.append(
                datalist
            )

        return JsonResponse({"data": datalists})
    else:
        raise PermissionDenied


def DataFile(request, server, dataname):
    """数据库备份文件目录"""
    if not request.user.is_authenticated:
        raise PermissionDenied
    elif "HTTP_REFERER" not in request.META:
        raise PermissionDenied
    elif settings.REFERER[0] in request.META['HTTP_REFERER']  or settings.REFERER[1] in request.META['HTTP_REFERER']:
        dataid = ''
        if dataname == "sqlserver":
            dataid = 0
        elif dataname == "mongodb":
            dataid = 1
        elif dataname == "postgresql":
            dataid = 2

        # 登陆服务器
        server = Server.objects.get(name=server)
        filename = DataName.objects.filter(server=server).get(name=dataid)
        if server.loginmode == 0:
            client = SSHAgent(server.address, server.port, server.user, server.password)
        else:
            client = SSHAgent(server.address, server.port, server.user, pkeyfile=server.keyfile)
        # 获取备份日期和路径
        timelist = client.findPath(filename.backuppath)

        return JsonResponse({"data": timelist})
    else:
        raise PermissionDenied
