import tkinter.filedialog  # must before tk
import tkinter as tk
from tkinter import ttk
from AdbInterface import AdbConnect
from pathlib import Path
# from TransferManager import TransferManager


class UI:

    def __init__(self):
        self.ip_addr = '0.0.0.0'
        self.adb_connect = AdbConnect(self.ip_addr)

        self.window = tk.Tk()
        self.window.title('Adb File Client')
        self.window.geometry('657x737')

        def shutdown():
            self.adb_connect.disconnect()
            self.window.destroy()
        self.window.protocol('WM_DELETE_WINDOW', shutdown)

        self.remote_dir = None
        self.push_file_num = None
        self.push_file_list = None
        self.down_dir_label = None
        self.files_listbox = None

        # self.t_m = TransferManager()
        self.tab_parent = ttk.Notebook(self.window)
        self.tab_file()
        self.tab_transfer()

    def tab_file(self):
        tab_file_browser = ttk.Frame(self.tab_parent)
        self.tab_parent.add(tab_file_browser, text="File")

        ip_entry = tk.Entry(tab_file_browser, font='Consolas', width=16)
        ip_entry.insert(tk.END, '192.168.137.105')
        ip_entry.place(x=0, y=0)
        connection_button = tk.Button(tab_file_browser, text='Connect', font='Consolas', width=10)

        def connect():
            self.ip_addr = ip = ip_entry.get()
            self.adb_connect.set_ip(ip)
            self.adb_connect.connect()
            connection_button.configure(text='Disconnect', command=disconnect)
            self.remote_dir.insert(tk.END, self.adb_connect.current_dir)
            # self.t_m.set_function(
            #     upload_function=self.adb_connect.device.push,
            #     download_function=self.adb_connect.device.pull
            # )
            update_files()

        def disconnect():
            self.adb_connect.disconnect()
            connection_button.configure(text='Connect', command=connect)
            self.remote_dir.delete(0, tk.END)
            self.files_listbox.delete(0, tk.END)

        connection_button.configure(command=connect)
        connection_button.place(x=149, y=0, height=23)

        self.remote_dir = tk.Entry(tab_file_browser, font='Consolas', width=44)
        self.remote_dir.place(x=249, y=0)

        def select_files():
            filenames = tk.filedialog.askopenfilenames()  # return '' when no files
            if type(filenames) == tuple:
                for filename in filenames:
                    if filename not in self.push_file_list['values']:
                        self.push_file_list['values'] = (*self.push_file_list['values'], filename)
            self.push_file_num.set('\t'+str(len(self.push_file_list['values']))+' file(s)')
        push_select_file_btn = tk.Button(tab_file_browser, text='上传文件', command=select_files)
        push_select_file_btn.place(x=0, y=25, height=21)

        self.push_file_num = tk.StringVar()
        self.push_file_list = ttk.Combobox(tab_file_browser, textvariable=self.push_file_num, width=57)
        self.push_file_list.place(x=65, y=25, height=21)

        def upload_all():
            if connection_button['text'][0] is 'D':
                # for f in self.push_file_list['values']:
                self.adb_connect.thread_upload(self.push_file_list['values'])
                clear_files()
        total_push = tk.Button(tab_file_browser, text='上传', command=upload_all)
        total_push.place(x=561, y=25, height=21)

        def clear_files():
            self.push_file_list['values'] = ()
            self.push_file_num.set('\t0 Files')
        total_clear = tk.Button(tab_file_browser, text='清空', command=clear_files)
        total_clear.place(x=613, y=25, height=21)

        def select_down_dir():
            d = tk.filedialog.askdirectory()
            if d != '':
                self.down_dir_label['text'] = d
                self.adb_connect.current_down_dir = d
        down_dir_btn = tk.Button(tab_file_browser, text='下载目录', command=select_down_dir)
        down_dir_btn.place(x=0, y=49, height=21)
        self.down_dir_label = tk.Label(tab_file_browser, text=self.adb_connect.default_download_dir)
        self.down_dir_label.place(x=65, y=49, height=21)

        def update_files():
            if Path(self.adb_connect.current_dir).as_posix() == Path(self.adb_connect.user_root).as_posix():
                self.adb_connect.dirs = self.adb_connect.dirs[2:]
            for dir_name in self.adb_connect.dirs:
                self.files_listbox.insert(tk.END, dir_name)
                self.files_listbox.itemconfig(tk.END, fg="#1453AD")
            for file_name in self.adb_connect.files:
                self.files_listbox.insert(tk.END, file_name)

        def change_directory(dirname):
            self.files_listbox.delete(0, tk.END)
            self.adb_connect.change_directory(dirname)
            self.remote_dir.delete(0, tk.END)
            self.remote_dir.insert(tk.END, self.adb_connect.current_dir)
            self.remote_dir.xview_moveto(1)  # right end

        def download_or_cd(_):
            name = self.files_listbox.get(self.files_listbox.curselection())
            if name in self.adb_connect.dirs:
                change_directory(name)
                update_files()
            else:
                # download it to desktop
                self.adb_connect.pull_file(name)
                pass
        filelist_frame = tk.Frame(tab_file_browser, width=81, height=31)
        filelist_frame.place(x=0, y=73)
        scrollbar = tk.Scrollbar(filelist_frame)
        self.files_listbox = tk.Listbox(filelist_frame, width=79, height=31, yscrollcommand=scrollbar.set)
        self.files_listbox.bind('<Double-Button-1>', download_or_cd)
        self.files_listbox.pack(side='left')
        scrollbar.pack(side="right", fill="y")
        scrollbar.config(command=self.files_listbox.yview)

    def tab_transfer(self):
        tab_transfer_browser = ttk.Frame(self.tab_parent)
        self.tab_parent.add(tab_transfer_browser, text="Transfer")
        self.tab_parent.pack(expand=1, fill='both')
