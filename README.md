# smbclient

## Samba installation on U20  

```
$ sudo apt install samba
```

## smb.conf

```
sudo nano /etc/samba/smb.conf
```

```
[share_folder]
comment = u20 samba share folder
path = /home/orisol/Code/khoo_share/
browseable = yes
read only = no
writable = yes
valid user = orisol,khoo
```

## samba username & password
```
sudo smbpasswd -a orisol
```
>> enter SMB password

## samba service stop and restart
```
sudo service smbd stop
```

```
sudo service smdb restart
```

## ifconfig
```
ifconfig
```
>> inet (ip address)
-----------------

## client
```
sudo apt install smbclient
```

## check smbclient
```
smbclient --version
```

## check share folder
```
smbclient -L //192.168.1.106 -U orisol
```

## login
```
smbclient //192.168.1.106/smb_share -U orisol
```

## smb command: ls
```
smb: \>   ls
```

## smb command: get (download file from server)
```
smb: \> get filename.xxx
```

## smb command: put (upload file from local)
```
smb: \> put /home/orisol/Desktop/xx.jpg
```


# python pip
>> conda env:
```
pip install pysmb
```