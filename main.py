
from __future__ import print_function, unicode_literals
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
import os
import requests
import subprocess
import sys
from loguru import logger
from user import run

logger.remove()
log_format = "<level>{level}</level>: <level>{message}</level>"
logger.add(sys.stdout, format=log_format)
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
    logger.info("FTP da khoi dong")
    
def stopFTP():
    subprocess.check_call(["sh", "-c", "systemctl stop vsftpd"],stdout=subprocess.DEVNULL)
    logger.info("FTP da dung lai")
    
def removeFTP():
    subprocess.check_call(["sh", "-c", "yum remove vsftpd -y"],stdout=subprocess.DEVNULL)
    logger.info("FTP da bi go bo")
    

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
    logger.info("Da khoi tao file cau hinh")
def setupFTP():
    subprocess.check_call(["sh", "-c", "yum install vsftpd -y"],stdout=subprocess.DEVNULL)
    subprocess.check_call(["sh", "-c", "systemctl enable vsftpd"],stdout=subprocess.DEVNULL)
    subprocess.check_call(["sh", "-c", "systemctl start vsftpd"],stdout=subprocess.DEVNULL)
    logger.info("FTP da duoc cai dat va khoi dong")
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
    "Cai dat FTP": setupFTP,
    "Khoi dong FTP": startFTP,
    "Dung FTP": stopFTP,
    "Go bo FTP": removeFTP,
    "Xem cau hinh FTP": viewConfig,
    "Quan ly user": run,
}


def main():
    while True:
        if not isCentos() :
            logger.error("This script only support CentOS")
            return
        if not isRoot():
            logger.error("Please run this script as root")
            return
        if not isHasInternet():
            logger.error("Please check your internet connection")
            return
        selections = ["Quan ly user","Quan ly file","Xem log"]
        logger.info("Kiem tra FTP")
        if isFTPInstalled():
            selections.insert(0, "Go bo FTP")
            selections.insert(1, "Xem cau hinh FTP")
            if isFTPRunning():
                selections.insert(1, "Dung FTP")
            else:
                selections.insert(1, "Khoi dong FTP")
                
        else:
            selections = ["Cai dat FTP"]
            
            
            
        choice =Choice(value=None,name="Thoat")
        selections.append(choice)
        action = inquirer.rawlist(
            message="Chon chuc nang",
            choices=selections,
            default=None
        ).execute()
        
        action_func = ACTION_MAP.get(action)
        if action_func:
            action_func()
        else:
            logger.info("Thoat chuong trinh")
            return
    

if __name__ == "__main__":
    main()