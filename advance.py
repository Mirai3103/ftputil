
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
    stat.S_IXUSR: "Chủ sở hữu có quyền thực thi",
    stat.S_IRGRP: "Nhóm có quyền đọc",
    stat.S_IWGRP: "Nhóm có quyền ghi",
    stat.S_IXGRP: "Nhóm có quyền thực thi",
    stat.S_IROTH: "Người khác có quyền đọc",
    stat.S_IWOTH: "Người khác có quyền ghi",
    stat.S_IXOTH: "Người khác có quyền thực thi"
}
PEM_CHOICES = [
    Choice(stat.S_IRUSR, "Chủ sở hữu có quyền đọc"),
    Choice(stat.S_IWUSR, "Chủ sở hữu có quyền ghi"),
    Choice(stat.S_IXUSR, "Chủ sở hữu có quyền thực thi"),
    Choice(stat.S_IRGRP, "Nhóm có quyền đọc"),
    Choice(stat.S_IWGRP, "Nhóm có quyền ghi"),
    Choice(stat.S_IXGRP, "Nhóm có quyền thực thi"),
    Choice(stat.S_IROTH, "Người khác có quyền đọc"),
    Choice(stat.S_IWOTH, "Người khác có quyền ghi"),
    Choice(stat.S_IXOTH, "Người khác có quyền thực thi")
]
PEM_MAP_TO_UNIX = {
    stat.S_IRUSR: 400,
    stat.S_IWUSR: 200,
    stat.S_IXUSR: 100,
    stat.S_IRGRP: 40,
    stat.S_IWGRP: 20,
    stat.S_IXGRP: 10,
    stat.S_IROTH: 4,
    stat.S_IWOTH: 2,
    stat.S_IXOTH: 1
}
def getUnixPermission(permissions):
    result = 0
    for p in permissions:
        result += PEM_MAP_TO_UNIX[p]
    if result < 10:
        return f"00{result}"
    if result < 100:
        return f"0{result}"
    return result



def getPermissionsChoice(path):
    st = os.stat(path)
    # copy list
    choices = PEM_CHOICES.copy()
    for key in PERMISSIONS_DISPLAY_DICT:
        if st.st_mode & key:
            for choice in choices:
                if choice.value == key:
                    choice.enabled = True
                    break
    return choices

def changeFolderPermission():
    path = inquirer.filepath(message="Nhập đường dẫn thư mục", validate=lambda result: os.path.isdir(result) or "Đường dẫn không tồn tại", default='~/').execute()

    print("Cập nhật quyền truy cập")
    permission = inquirer.checkbox(
        message="Chọn quyền truy cập",
        choices=getPermissionsChoice(path),
        validate=lambda result: len(result) > 0 or "Chọn ít nhất một quyền"
    ).execute()
    perm = 0
    for p in permission:
        perm |= p
    unixCode =getUnixPermission(permissions=permission)
    isApplyToAll = inquirer.confirm(message="Áp dụng cho tất cả thư mục con", default=False).execute()
    if isApplyToAll:
        subprocess.check_call(["sh", "-c", f"chmod -R {unixCode} {path}"],stdout=subprocess.PIPE)
    else:
        os.chmod(path, perm)


