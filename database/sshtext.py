from paramiko import SSHClient, AutoAddPolicy
from paramiko import SFTPClient, RSAKey
from paramiko import Transport
from datetime import datetime
from os.path import split, exists

import os


class SSHAgent(object):
    """远程还原"""
    def __init__(self, host, port=1022, user="feidao", password="fdcf@2020", pkey=''):
        """初始化
        
        :param host: 远程主机
        :param port: 远程端口
        :param user: 远程用户
        :param password: 远程密码
        """
        self.transport = Transport((host, port))
        if pkey:
            pkey = RSAKey.from_private_key_file(pkey)
            self.transport.connect(
                username=user,
                pkey=pkey,
            )
        else:
            self.transport.connect(
                username=user,
                password=password,
            )
        self.SFTP = SFTPClient.from_transport(self.transport)

    def runCommand(self, command):
        client = SSHClient()
        client._transport = self.transport

        return client.exec_command(command)

    def backupFile(self, path):
        """确认备份文件和数据库"""
        datapath, dataname = split(path)
        datafile = ''
        if dataname == "mssql":
            datafile = 'pcb_biz.bak'
        elif dataname == 'pg':
            datafile = 'pcb_erp_clientmeta.out'
        elif dataname == 'mongo':
            datafile = 'pcb_erp_file'

        return (datafile, dataname)


    def findPath(self, path):
        """返回备份日期
        
        :param path: 需要查询的路径
        """
        datafile = self.backupFile(path)
        nameLists = list()
        backname = ''
        timelists = list()

        try:
            for patnName in self.SFTP.listdir(path=path):
                if "tar.gz" in patnName:
                    continue
                elif patnName.startswith(datafile[1]) == False:
                    continue

                backupfile = self.SFTP.listdir("{}/{}".format(path, patnName))
                if datafile[0] not in backupfile:
                    # print(patnName)
                    continue

                backname, backtime = patnName.split('_')
                timelists.append(backtime)

            timelists.sort(reverse = True)  # 降序排列
            for dateStr in timelists:
                backtime = datetime.strptime(
                    dateStr, "%Y%m%d%H%M%S").strftime("%Y年%m月%d日 %H:%M:%S"
                )
                nameLists.append([f"{backname}_{dateStr}", backtime])
        except:
            if exists(path) == False:
                os.makedirs(path)
            nameLists = []
        
        return nameLists if len(nameLists) > 1 else [["", "此服务器没有备份"],]
        

run = SSHAgent(host="182.101.207.117", pkey="/home/feidao/.ssh/zhaohonglive.pub")
for i in run.findPath("/data/backup/file/mssql/"):
    print(i)
