import unittest
from ftplib import FTP
from user import replaceUserToFtp
import os
import stat
class TestExample(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestExample, self).__init__(*args, **kwargs)
        self.usertest = "utest1"
        self.passtest = "123456"
        replaceUserToFtp([self.usertest,'anonymous'])
    
    def test_connect_ftp(self):
        print('run 0')
        ftp = FTP("localhost")
        ftp.login("anonymous", "anonymous")
        ftp.quit()
        self.assertTrue(True)
        print('run 0 done')
    def setUp(self):
        os.system(f"useradd {self.usertest}")
        os.system(f"echo {self.passtest} | passwd {self.usertest} --stdin")
    
    def tearDown(self):
        os.system("userdel "+self.usertest)
        os.system("rm -rf /home/"+self.usertest)
    
    def test_user_can_login(self):
        print('run 1')
        try:
            ftp = FTP("localhost")
            ftp.login(self.usertest, self.passtest)
            ftp.quit()
            self.assertTrue(True)
        except Exception as e:
            self.assertTrue(False)
        print('run 1 done')
    def test_user_with_wrong_password(self):
        print('run 2')
        ftp = FTP("localhost")
        try:
            ftp.login(self.usertest, "wrongpassword")
            assert False
        except Exception as e:
            self.assertTrue(True)
        ftp.quit()
        print('run 2 done')
    
    def testUser1CanUploadToUser1Home(self):
        print('run 3')
        filePath ="./test.txt"
        ftp = FTP("localhost")
        ftp.login(self.usertest, self.passtest)
        with open(filePath, "rb") as f:
            ftp.storbinary("STOR test.txt", f)
        ftp.quit()
        self.assertTrue(True)

        print('run 3 done')
    def testCanNotUpload(self):
        filePath ="./test.txt"
        permission = stat.S_IRUSR | stat.S_IXUSR #chỉ có quyền đọc và thực thi
        
        print(os.stat(filePath))
        os.chmod(filePath, permission)
        ftp = FTP("localhost")
        ftp.login(self.usertest, self.passtest)
        try:
            with open(filePath, "rb") as f:
                ftp.storbinary("STOR test.txt", f)
            self.assertTrue(False)
        except Exception as e:
            print(e)
            self.assertTrue(True)
        ftp.quit()
        self.assertTrue( not os.path.exists(filePath))
        os.system("chmod 777 "+filePath)

if __name__ == "__main__":
    unittest.main()
