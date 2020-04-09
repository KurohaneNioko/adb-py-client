from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
from pathlib import Path
import os
import re
import sys
import copy
import threading


class UploadThread (threading.Thread):

    def __init__(self, f, filenames, remote_dir):
        threading.Thread.__init__(self)
        # self.thread_id = thread_id
        self.push_function = f
        self.filenames = copy.deepcopy(filenames)
        self.remote_dir = remote_dir

    def run(self):
        print(self.filenames)
        for filename in self.filenames:
            self.push_function(filename, Path(os.path.join(self.remote_dir, filename.split('/')[-1])).as_posix())
            print('Upload ', filename, 'Done')


class DownloadThread (threading.Thread):

    def __init__(self, f, filename, local_dir):
        threading.Thread.__init__(self)
        # self.thread_id = thread_id
        self.pull_function = f
        self.filename = filename
        self.local_dir = local_dir

    def run(self):
        self.pull_function(self.filename, Path(os.path.join(self.local_dir, self.filename.split('/')[-1])).as_posix())
        print('Download ', self.filename, 'Done')


# arp -a -> show ip & device
class AdbConnect:

    def __init__(self, ip):
        self.ip = ip
        self.device = None
        self.user_root = '/storage/emulated/0/'
        self.current_dir = None
        self.dirs = []
        self.files = []
        if sys.platform.startswith('win'):
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
            self.default_download_dir = Path(winreg.QueryValueEx(key, "Desktop")[0]).as_posix()
        else:
            self.default_download_dir = os.path.expanduser('~')
        self.current_down_dir = self.default_download_dir

    def set_ip(self, ip):
        self.ip = ip

    def connect(self):
        with open(os.path.join(os.path.expanduser('~'), '.android/adbkey')) as f:
            p = f.read()
        signer = PythonRSASigner('', p)
        self.device = AdbDeviceTcp(self.ip, 5555, default_timeout_s=9.)
        self.device.connect(rsa_keys=[signer], auth_timeout_s=0.1)
        # ls -l
        self.ls()
        print('connect')

    def disconnect(self):
        if self.device is not None:
            self.device.close()
        print('close')

    def check_dir_or_file(self, names):
        detailed_names = re.split('\n', names)[1:-1]
        # print(detailed_names)
        # 7 -> support space in filename
        self.dirs, self.files = [], []
        for e in detailed_names:
            if e.startswith('d'):
                self.dirs.append(re.split('\s+', e, maxsplit=7)[-1])
            else:
                self.files.append(re.split('\s+', e, maxsplit=7)[-1])

    def ls(self, dir_name=None):
        if dir_name is None:
            self.current_dir = self.user_root
        else:
            self.current_dir = dir_name
        dir_file_names = self.device.shell('ls -la "' + self.current_dir + '"')
        self.check_dir_or_file(dir_file_names)
        # print('dirs', self.dirs, 'files', self.files, sep='\n')

    def change_directory(self, dir_name):
        if dir_name == '.':
            # do nothing
            pass
        elif dir_name == '..':
            self.current_dir = Path(self.current_dir).parent.as_posix()
        else:
            self.current_dir = Path(os.path.join(self.current_dir, dir_name)).as_posix()
        self.ls(self.current_dir)
        # print(self.current_dir, 'dirs', self.dirs, 'files', self.files, sep='\n')

    def pull_file(self, filename):
        download_dir = self.current_down_dir
        d_thread = DownloadThread(f=self.device.pull, filename=Path(os.path.join(self.current_dir, filename)).as_posix(), local_dir=download_dir)
        d_thread.start()
        # self.device.pull(
        #     Path(os.path.join(self.current_dir, filename)).as_posix(),
        #     os.path.join(download_dir, filename)
        # )

    def thread_upload(self, local_files):
        # remote_dir -> current dir
        u_thread = UploadThread(f=self.device.push, filenames=local_files, remote_dir=self.current_dir)
        u_thread.start()
        # for e in local_files:
        #     self.device.push(e, Path(os.path.join(self.current_dir,e.split('/')[-1])).as_posix())
