import sys
import time
import os
from smb.SMBConnection import SMBConnection
from smb.base import SMB, NotConnectedError, NotReadyError, SMBTimeout
import smb.smb_constants
from smb.base import SharedFile

g_ignore_service_name = ['print$', 'IPC$']


class SmbClient():
    def __init__(self):
        pass

    def init_parameter(self, ip, username, password, port=445):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.conn_timeout = 5
        self.data_timeout = 10
        self.conn = None
        self.status = False

    def connect(self):
        # if ip not exist:
        # error: timed out
        # error: Not connected to server
        # error: [Errno 113] No route to host

        status = True
        try:
            self.conn = SMBConnection(
                self.username, self.password, '', '', use_ntlm_v2=True)
            self.conn.connect(self.ip, self.port, timeout=self.conn_timeout)
            self.status = True
        except Exception as e:
            print('error:', e)
            self.conn.close()
            status = False
        finally:
            return status

    def disconnect(self):
        self.conn.close()

    def get_service_name(self):
        status = True
        services = []
        try:
            for service in self.conn.listShares():
                services.append(service.name)
        except Exception as e:
            print('error:', e)
            status = False
        finally:
            if status == True and len(services) > 0:
                for service in services:
                    if service in g_ignore_service_name:
                        services.remove(service)
            else:
                status = False
        return status, services

    def get_filenames(self, service_name, folder_name):
        status = True
        filenames = []
        try:
            for f_name in self.conn.listPath(service_name, folder_name,
                                             search=smb.smb_constants.SMB_FILE_ATTRIBUTE_ARCHIVE |
                                             smb.smb_constants.SMB_FILE_ATTRIBUTE_INCL_NORMAL
                                             ):
                if f_name.filename[0] != '.':
                    filenames.append(f_name.filename)
        except Exception as e:
            print('error:', e)
            status = False
        finally:
            return status, filenames

    def download(self, filenames, service_name, smb_dir, local_dir):
        if isinstance(filenames, list):
            for filename in filenames:
                dest_filename = os.path.join(local_dir, filename)
                sour_filename = os.path.join(smb_dir, filename)
                local_file = open(dest_filename, 'wb')
                self.conn.retrieveFile(service_name, sour_filename, local_file)
                local_file.close()

    def upload(self, filenames, service_name, smb_dir, local_dir):
        # the smb_dir must be already exists
        if isinstance(filenames, list):
            for filename in filenames:
                sour_filename = os.path.join(local_dir, filename)
                dest_filename = os.path.join(smb_dir, filename)
                local_file = open(sour_filename, 'rb')
                self.conn.storeFile(service_name, dest_filename, local_file)
                local_file.close()

    def mkdir(self, service_name, path):
        # before mkdir, check folder exist or not.
        try:
            self.conn.createDirectory(service_name, path)
        except Exception as e:
            print(e)

    def rmdir(self, service_name, path):
        # before rmdir, check folder exist or not.
        try:
            self.conn.deleteDirectory(service_name, path)
        except Exception as e:
            print(e)

    def rmfiles(self, service_name, path):
        # path with *, e.g. *.ini, or uhf*
        try:
            self.conn.deleteFiles(service_name, path,
                                  delete_matching_folders=True)
        except Exception as e:
            print(e)

    def rename(self, service_name, old_name, new_name):
        # before , check folder exist or not.
        try:
            self.conn.rename(service_name, old_name, new_name)
        except Exception as e:
            print(e)

    def get_attributes(self, service_name, path):
        attr = self.conn.getAttributes(service_name, path)
        return attr

    def echo(self, str_data):
        resp = self.conn.echo(str_data)
        return resp


def main():
    # real ipc
    # ip = '192.168.1.106'
    # username = 'orisol'
    # password = 'orisol'

    # vm test
    ip = '192.168.56.106'
    username = 'khoo'
    password = 'khoo'
    sharefolder_service = ''
    download_filelist = []
    curr_local_dir = os.getcwd()

    upload_dir = os.path.join(curr_local_dir, 'k1')
    upload_file_list = []

    file_list = []
    dir_list = []
    for dirPath, dirNames, fileNames in os.walk(curr_local_dir):
        fileNames = [f for f in fileNames if not f[0] == '.']
        dirNames[:] = [d for d in dirNames if not d[0] == '.']
        file_list.append(fileNames)
        dir_list.append(dirNames)
    if len(file_list[1]) > 0:
        upload_file_list = file_list[1]

    print(upload_dir)
    print('upload_file_list:', upload_file_list)
    # print('file_list:',file_list)
    # print('dir_list:',dir_list)

    samba_client = SmbClient()
    samba_client.init_parameter(ip=ip, username=username, password=password)
    status = samba_client.connect()
    print('status:', status)

    status_service_name = samba_client.get_service_name()
    # print('status_service_name:', status_service_name)

    if status_service_name[0]:
        sharefolder_service = status_service_name[1][0]

    # status_service_file_list = samba_client.get_filenames(
    #     sharefolder_service, '/')
    # if status_service_file_list[0]:
    #     download_filelist = status_service_file_list[1]
    #     samba_client.download(download_filelist,sharefolder_service, '/', curr_local_dir)

        # create_folder = 'ktest'
        # samba_client.mkdir(sharefolder_service,create_folder)
        # samba_client.upload(upload_file_list,sharefolder_service,os.path.join('/', create_folder) , upload_dir)

        # samba_client.rmdir(sharefolder_service,'folder_1')

        # samba_client.rmfiles(sharefolder_service,'ttt/int*')

    # samba_client.rename(sharefolder_service,'/vvv1/omashita','/vvv1/omashita.5566')
    attr = samba_client.get_attributes(sharefolder_service, '/sample.ini')
    print('attr-size:', attr.file_size)
    print('attr-filename :', attr.filename)
    print('attr-isDirectory :', attr.isDirectory)

    attr = samba_client.get_attributes(sharefolder_service, '/vvv1')
    print('attr-isDirectory :', attr.isDirectory)

    echo_resp = samba_client.echo('hello world')
    print('echo_resp:', echo_resp)

    print('end of process, ----hello orisol')
    samba_client.disconnect()


if __name__ == '__main__':
    main()
