
from __future__ import print_function, unicode_literals
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
import os
import requests
import subprocess
from user import run

# https://github.com/kazhala/InquirerPy
def isHasInternet():
    url = "https://www.google.com"
    timeout = 5
    try:
        request = requests.get(url, timeout=timeout)
        return True
    except (requests.ConnectionError, requests.Timeout) as exception:
        return False

def isCentos():
    try:
        subprocess.check_call(["yum", "--version"],stdout=subprocess.DEVNULL)
        return True
    except:
        return False

def isFTPInstalled():
    try:
        subprocess.check_call(["sh", "-c", "rpm -q vsftpd"],stdout=subprocess.DEVNULL)
        return True
    except:
        return False

def isFTPRunning():
    try:
        subprocess.check_call(["sh", "-c", "systemctl is-active vsftpd"],stdout=subprocess.DEVNULL)
        return True
    except:
        return False
    
def startFTP():
    subprocess.check_call(["sh", "-c", "systemctl start vsftpd"],stdout=subprocess.DEVNULL)
    print("FTP đã khởi động")
    
def stopFTP():
    subprocess.check_call(["sh", "-c", "systemctl stop vsftpd"],stdout=subprocess.DEVNULL)
    print("FTP đã dừng")
    
def removeFTP():
    subprocess.check_call(["sh", "-c", "yum remove vsftpd -y"],stdout=subprocess.DEVNULL)
    print("FTP đã được gỡ bỏ")
    

def isRoot():
    return os.getegid() == 0

def initConfig():
    #  replace listen=NO with listen=YES
    with open("/etc/vsftpd/vsftpd.conf", "r") as f:
        lines = f.readlines()
    with open("/etc/vsftpd/vsftpd.conf", "w") as f:
        for line in lines:
            if  line.startswith("#listen=") or line.startswith("listen-"):
                f.write("listen=YES\n")
            elif line.startswith("#listen_ipv6") or line.startswith("listen_ipv6"):
                f.write("listen_ipv6=NO\n")
            elif line.startswith("#anonymous_enable") or line.startswith("anonymous_enable"):
                f.write("anonymous_enable=YES\n")
            else:
                f.write(line)
    print("Đã cấu hình xong")
def setupFTP():
    subprocess.check_call(["sh", "-c", "yum install vsftpd -y"],stdout=subprocess.DEVNULL)
    subprocess.check_call(["sh", "-c", "systemctl enable vsftpd"],stdout=subprocess.DEVNULL)
    subprocess.check_call(["sh", "-c", "systemctl start vsftpd"],stdout=subprocess.DEVNULL)
    print("FTP đã được cài đặt và khởi động")
    initConfig()



def viewConfig():
    with open("/etc/vsftpd/vsftpd.conf", "r") as f:
        lines = f.readlines()
    i = 0
    for line in lines:
        if "#" in line:
            continue
        print(f"{line}",end="")
        i += 1

ACTION_MAP = {
    "Cài đặt FTP": setupFTP,
    "Khởi động FTP": startFTP,
    "Dừng FTP": stopFTP,
    "Gỡ bỏ FTP": removeFTP,
    "Xem cấu hình FTP": viewConfig,
    "Quản lý user": run,
}

def main():
    while True:
        if not isCentos() :
            print("Script này chỉ hỗ trợ CentOS")
            return
        if not isRoot():
            print("Vui lòng chạy script này với quyền root")
            return
        if not isHasInternet():
            print("Vui lòng kiểm tra kết nối internet của bạn")
            return
        selections = ["Quản lý user", "Quản lý file", "Xem log"]
        print("Kiểm tra FTP")
        if isFTPInstalled():
            selections.insert(0, "Gỡ bỏ FTP")
            selections.insert(1, "Xem cấu hình FTP")
            if isFTPRunning():
                selections.insert(1, "Dừng FTP")
            else:
                selections.insert(1, "Khởi động FTP")
        else:
            selections = ["Cài đặt FTP"]
        choice =Choice(value=None,name="Thoát")
        selections.append(choice)
        action = inquirer.rawlist(
            message="Chọn chức năng",
            choices=selections,
            default=None
        ).execute()
        
        action_func = ACTION_MAP.get(action)
        if action_func:
            action_func()
        else:
            print("Thoát")
            return
    

if __name__ == "__main__":
    main()