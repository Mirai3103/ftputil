
from __future__ import print_function, unicode_literals

from util import changeOrAddConfig, getConfig
from InquirerPy import inquirer
import os
from InquirerPy.base.control import Choice
import stat
import subprocess


PERMISSIONS_DISPLAY_DICT = {
    stat.S_IRUSR: "Chủ sở hữu có quyền đọc",
    stat.S_IWUSR: "Chủ sở hữu có quyền ghi",
    stat.S_IXUSR: "Chủ sở hữu có quyền truy cập",
    stat.S_IRGRP: "Nhóm có quyền đọc",
    stat.S_IWGRP: "Nhóm có quyền ghi",
    stat.S_IXGRP: "Nhóm có quyền truy cập",
    stat.S_IROTH: "Người khác có quyền đọc",
    stat.S_IWOTH: "Người khác có quyền ghi",
    stat.S_IXOTH: "Người khác có quyền truy cập"
}
PEM_CHOICES = [
    Choice(stat.S_IRUSR, "Chủ sở hữu có quyền đọc"),
    Choice(stat.S_IWUSR, "Chủ sở hữu có quyền ghi"),
    Choice(stat.S_IXUSR, "Chủ sở hữu có quyền truy cập"),
    Choice(stat.S_IRGRP, "Nhóm có quyền đọc"),
    Choice(stat.S_IWGRP, "Nhóm có quyền ghi"),
    Choice(stat.S_IXGRP, "Nhóm có quyền truy cập"),
    Choice(stat.S_IROTH, "Người khác có quyền đọc"),
    Choice(stat.S_IWOTH, "Người khác có quyền ghi"),
    Choice(stat.S_IXOTH, "Người khác có quyền truy cập")
]




def getPermissionsChoice(path):
    st = os.stat(path)
    # copy list
    choices = PEM_CHOICES.copy()
    for choice in choices:
        choice.enabled = False
    for key in PERMISSIONS_DISPLAY_DICT:
        if st.st_mode & key:
            for choice in choices:
                if choice.value == key:
                    choice.enabled = True
                    break
    return choices

def changeFolderPermission(path= None):
    if path is None:
        path =inquirer.filepath(message="Nhập đường dẫn thư mục", validate=lambda result: os.path.isdir(result) or "Đường dẫn không tồn tại", default='~/').execute()
    print("Cập nhật quyền truy cập")
    permission = inquirer.checkbox(
        message="Chọn quyền truy cập",
        choices=getPermissionsChoice(path),
        validate=lambda result: len(result) > 0 or "Chọn ít nhất một quyền"
    ).execute()
    perm = 0
    for p in permission:
        perm |= p
    isApplyToAll = inquirer.confirm(message="Áp dụng cho tất cả thư mục con", default=False).execute()
    os.chmod(path, perm)
    if isApplyToAll:
        changeFolderPermissionRecursively(path, perm)
        

def changeFolderPermissionRecursively(path, perm):
    for root, dirs, files in os.walk(path):
        for d in dirs:
            os.chmod(os.path.join(root, d), perm)
        for f in files:
            os.chmod(os.path.join(root, f), perm)
    print(f"Tất cả thư mục con của {path} đã được cập nhật quyền truy cập")


def getListGroup():
    groups = []
    with open("/etc/group", "r") as f:
        lines = f.readlines()
    for line in lines:
        groups.append(line.split(":")[0])
    return groups

def getListUser():
    users = []
    with open("/etc/passwd", "r") as f:
        lines = f.readlines()
    for line in lines:
        users.append(line.split(":")[0])
    return users
def getListUserOfGroup(group):
    usersId = []
    with open("/etc/group", "r") as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith(group):
            usersId = line.split(":")[2]
            break
    users = []
    with open("/etc/passwd", "r") as f:
        lines = f.readlines()
    for line in lines:
        if line.split(":")[2] in usersId:
            users.append(line.split(":")[0])
    return users


def createFolder():
    path = inquirer.filepath(message="Nhập đường dẫn thư mục", validate=lambda result: not os.path.exists(result) or "Thư mục đã tồn tại").execute()
    os.makedirs(path)
    print(f"Thư mục {path} đã được tạo")
    print("Bạn có muốn cập nhật quyền truy cập không?")
    isChangePermission = inquirer.confirm(message="Cập nhật quyền truy cập", default=True).execute()
    if isChangePermission:
        changeFolderPermission(path=path)
    # groupadd -g  group-name
def createGroup():
    group = inquirer.text(message="Nhập tên nhóm", validate=lambda result: len(result) > 0 or "Tên nhóm không được để trống").execute()
    subprocess.check_call(["sh", "-c", f"groupadd {group}"],stdout=subprocess.PIPE)
    print(f"Nhóm {group} đã được tạo")
    print("Bạn có muốn thêm người dùng vào nhóm không?")
    isAddUser = inquirer.confirm(message="Thêm người dùng vào nhóm", default=True).execute()
    if isAddUser:
        addUserToGroup(group)
        
def addUserToGroup(group=None):
    if group is None:
        group = inquirer.fuzzy(
            message="Chọn nhóm",
            choices=[Choice(x,x) for x in getListGroup()],
            default="",
            multiselect=False
        ).execute()
    choices= [Choice(x,x) for x in getListUser()]
    listUserOfGr = getListUserOfGroup(group)
    for user in listUserOfGr:
        for choice in choices:
            if choice.value == user:
                choice.enabled = True
                break
    selectedUser =inquirer.fuzzy(
        message="Select actions:",
        choices=choices,
        default="",
        multiselect=True
    ).execute()
    removeAllUserFromGroup(group)
    for user in selectedUser:
        subprocess.check_call(["sh", "-c", f"usermod -a -G {group} {user}"],stdout=subprocess.PIPE)
        print(f"Người dùng {user} đã được thêm vào nhóm {group}")
 
def removeAllUserFromGroup(group):
    users = getListUserOfGroup(group)
    for user in users:
        subprocess.check_call(["sh", "-c", f"gpasswd -d {user} {group}"],stdout=subprocess.PIPE)
    print(f"Tất cả người dùng đã được xóa khỏi nhóm {group}")
           
        
def folderOwner():
    path = inquirer.filepath(message="Nhập đường dẫn thư mục", validate=lambda result: os.path.isdir(result) or "Đường dẫn không tồn tại", default='~/').execute()
    owner = inquirer.fuzzy(
        message="Chọn người dùng",
        choices=[Choice(x,x) for x in getListUser()],
        default="",
        multiselect=False
    ).execute()
    
    subprocess.check_call(["sh", "-c", f"chown {owner} {path}"],stdout=subprocess.PIPE)
    print(f"Thư mục {path} đã được chuyển cho người dùng {owner}")

def folderGroup():
    path = inquirer.filepath(message="Nhập đường dẫn thư mục", validate=lambda result: os.path.isdir(result) or "Đường dẫn không tồn tại", default='~/').execute()
    group = inquirer.fuzzy(
        message="Chọn nhóm",
        choices=[Choice(x,x) for x in getListGroup()],
        default="",
        multiselect=False
    ).execute()
    
    subprocess.check_call(["sh", "-c", f"chgrp {group} {path}"],stdout=subprocess.PIPE)
    print(f"Thư mục {path} đã được chuyển cho nhóm {group}")
 

ACTION_CHOICES = [
    Choice("createFolder", "Tạo thư mục"),
    Choice("changeFolderPermission", "Thay đổi quyền truy cập thư mục"),
    Choice("createGroup", "Tạo nhóm"),
    Choice("addUserToGroup", "Thêm người dùng vào nhóm"),
    Choice("folderOwner", "Chuyển quyền sở hữu thư mục"),
    Choice("folderGroup", "Chuyển quyền nhóm thư mục"),
    Choice(None, "Thoát")
]

ACTIONS_MAP={
    "createFolder": createFolder,
    "changeFolderPermission": changeFolderPermission,
    "createGroup": createGroup,
    "addUserToGroup": addUserToGroup,
    "folderOwner": folderOwner,
    "folderGroup": folderGroup
}

def folderManager():
    while True:
        os.system('clear')
        action = inquirer.select(
            message="Chọn hành động",
            choices=ACTION_CHOICES,
            default=None,
            cycle=True,
        ).execute()
        if action is None:
            print("Thoát chương trình")
            return
        ACTIONS_MAP[action]()
        
if __name__ == "__main__":
    # folderManager()  
    changeFolderPermission()

    
    

