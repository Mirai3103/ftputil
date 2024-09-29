# 1. Quản lý User:
# Thêm user: Tạo một user mới cho FPT server.
# Xóa user: Xóa một user hiện có.
# Cập nhật thông tin user: Thay đổi thông tin của user (mật khẩu, quyền truy cập).
# Liệt kê user: Hiển thị danh sách tất cả các user trên server.

from __future__ import print_function, unicode_literals
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
import os
import requests
import subprocess
import sys
from loguru import logger
import stat
from util import changeOrAddConfig


chroot_list_path = "/etc/vsftpd/chroot_list"
    

def changeAnonymousUser():
    name = inquirer.filepath(message="Nhap duong dan thu muc chua file can chia se", validate=lambda result: os.path.isdir(result) or "Duong dan khong ton tai",default='~/').execute()
    permission = inquirer.checkbox(
        message="Chon quyen truy cap",

        choices=[
            Choice(stat.S_IROTH, " Read"),
            Choice(stat.S_IWOTH, " Write"),
            Choice(stat.S_IXOTH, " Execute"),
            Choice(stat.S_IROTH|stat.S_IWOTH|stat.S_IXOTH, "All" )
            
        ],
        default=[stat.S_IROTH],
        validate=lambda result: len(result) > 0 or "Chon it nhat 1 quyen"
    ).execute()
    #  nếu choice include all thì chỉ lấy all
    logger.info(f"Quyen truy cap: {permission}")
    perm = stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP 
    perm |= stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
    for p in permission:
            perm |= p
    if not os.path.exists(name):
      
        os.makedirs(name)
        logger.info(f"Thu muc {name} da duoc tao voi quyen {perm}")
    os.chmod(name, perm)
    changeOrAddConfig("anonymous_enable", "YES", "/etc/vsftpd/vsftpd.conf")
    changeOrAddConfig("anon_root", name, "/etc/vsftpd/vsftpd.conf")
    changeOrAddConfig("anon_upload_enable", "YES", "/etc/vsftpd/vsftpd.conf")
    changeOrAddConfig("anon_mkdir_write_enable", "YES", "/etc/vsftpd/vsftpd.conf")
    changeOrAddConfig("anon_other_write_enable", "YES", "/etc/vsftpd/vsftpd.conf")
    changeOrAddConfig("write_enable", "YES", "/etc/vsftpd/vsftpd.conf")
    changeOrAddConfig("allow_writeable_chroot", "YES", "/etc/vsftpd/vsftpd.conf")
    subprocess.check_call(["sh", "-c", "systemctl restart vsftpd"],stdout=subprocess.DEVNULL)
    logger.info("FTP da duoc khoi dong lai")
    
def turnOnAnonymousUser():
    changeOrAddConfig("anonymous_enable", "YES", "/etc/vsftpd/vsftpd.conf")
    subprocess.check_call(["sh", "-c", "systemctl restart vsftpd"],stdout=subprocess.DEVNULL)
    logger.info("FTP da duoc khoi dong lai")
def turnOffAnonymousUser():
    changeOrAddConfig("anonymous_enable", "NO", "/etc/vsftpd/vsftpd.conf")
    subprocess.check_call(["sh", "-c", "systemctl restart vsftpd"],stdout=subprocess.DEVNULL)
    logger.info("FTP da duoc khoi dong lai")

def enableLocalUser():
    changeOrAddConfig("chroot_local_user", "YES", "/etc/vsftpd/vsftpd.conf")
    changeOrAddConfig("chroot_list_enable", "YES", "/etc/vsftpd/vsftpd.conf")
    changeOrAddConfig("chroot_list_file", chroot_list_path, "/etc/vsftpd/vsftpd.conf")
    subprocess.check_call(["sh", "-c", "systemctl restart vsftpd"],stdout=subprocess.DEVNULL)
    logger.info("FTP da duoc khoi dong lai")
def getUserList():
    # lấy user từ passwd
    user_list = []
    with open("/etc/passwd", "r") as f:
        for line in f:
            user_list.append(line.split(":")[0])
    return user_list

def getFtpUserList():
    if not os.path.exists(chroot_list_path):
        with open(chroot_list_path, "w") as f:
            pass
    user_list = []
    with open(chroot_list_path, "r") as f:
        for line in f:
            user_list.append(line.strip())
    return user_list

def chooseUserToFtp():
    user_list = getUserList()
    ftp_user_list = getFtpUserList()
    #  tạo select để chọn user, danh sách user là user_list, default là user trong ftp_user_list
    user = inquirer.checkbox(
        message="Chon user",
        choices=[Choice(user, user) for user in user_list],
        default=[Choice(user, user) for user in ftp_user_list],
        cycle=True,
    ).execute()
    # join bang dau phay
    logger.info(f"Da chon user: {', '.join(user)}")
    # //todo: thêm user vào ftp
    replaceUserToFtp(user)
    return user

def addNewUser():
    # tạo user mới cho local
    user = inquirer.text(message="Nhap ten user", validate=lambda result: result not in getUserList() or "User da ton tai").execute()
    password = inquirer.secret(message="Nhap mat khau").execute()
    subprocess.check_call(["useradd", "-m", user],stdout=subprocess.DEVNULL)
    subprocess.check_call(["sh", "-c", f"echo {user}:{password} | chpasswd"],stdout=subprocess.DEVNULL)
    newUserId = subprocess.check_output(["id", "-u", user]).decode().strip()
    homeDir = inquirer.filepath(message="Nhap duong dan thu muc home", default=f"/home/{user}").execute()
    if not os.path.exists(homeDir):
        os.makedirs(homeDir)
    os.chown(homeDir, int(newUserId), -1)
    
    
    subprocess.check_call(["usermod","-m", "-d", homeDir, user],stdout=subprocess.DEVNULL)
    os.chmod(homeDir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    logger.info(f"Da tao user {user}")
    isYes = inquirer.confirm(message="Ban co muon them user nay vao FTP khong?",default=True).execute()
    if isYes:
        addUserToFtp([user])
def addUserToFtp(user):
    with open(chroot_list_path, "a") as f:
        for u in user:
            f.write(u + "\n")
    subprocess.check_call(["sh", "-c", "systemctl restart vsftpd"],stdout=subprocess.DEVNULL)
    logger.info("FTP da duoc khoi dong lai")
def replaceUserToFtp(user):
    with open(chroot_list_path, "w") as f:
        for u in user:
            f.write(u + "\n")
    subprocess.check_call(["sh", "-c", "systemctl restart vsftpd"],stdout=subprocess.DEVNULL)
    logger.info("FTP da duoc khoi dong lai")
    
def getConfig(key):
    with open("/etc/vsftpd/vsftpd.conf", "r") as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith(key+"="):
            return line.split("=")[1].strip()
    return None
    
ACTIONS_MAP = {
    "Them user": addNewUser,
    "Them/Xoa user FTP":  chooseUserToFtp,
    "Tat user anonymous": turnOffAnonymousUser,
    "Bat user anonymous": turnOnAnonymousUser,
    "Thay doi quyen truy cap anonymous": changeAnonymousUser
}

def run():
    
    while True:
        selections = ["Them/Xoa user FTP","Them user"]
        if getConfig("anonymous_enable") == "YES":
            selections.insert(0, "Tat user anonymous")
            selections.insert(1, "Thay doi quyen truy cap anonymous")
        else:
            selections.insert(0, "Bat user anonymous")
        if getConfig("chroot_local_user") != "YES":
            enableLocalUser()
        choice =Choice(value=None,name="Thoat")
        selections.append(choice)
        action = inquirer.select(
            message="Chon hanh dong",
            choices=selections,
            default=None,
            cycle=True,
        ).execute()
        if action is None:
            logger.info("Thoat quan ly user")
            return
        action = ACTIONS_MAP[action]
        action()
        
        

if __name__ == "__main__":
    run()