import sys
import time
from smb.SMBConnection import SMBConnection
from smb.base import SMB, NotConnectedError, NotReadyError, SMBTimeout
import smb.smb_constants


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


def main():
    ip = '192.168.1.106'
    username = 'orisol'
    password = 'orisol'
    samba_client = SmbClient()
    samba_client.init_parameter(ip=ip, username=username, password=password)
    status = samba_client.connect()
    print('status:', status)

    service_name = samba_client.get_service_name()
    print('service_name:', service_name)

    file_list = status = samba_client.get_filenames('smb_share', '/')
    print('file_list:', file_list)

    print('hello orisol')
    samba_client.disconnect()


if __name__ == '__main__':
    main()
