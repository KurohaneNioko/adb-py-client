from TkUI import UI

"""
==========================
SMALL FILES ONLY !!!!!!
==========================
py_adb_shell no threading for multi-files !!!
and not support asynchronous transfer (class in TransferManager.py)

TODO:
select device
progress percentage (file size)
cancelling transfer
===================
not to implement:
dir upload/download -> use samba tools plz
"""
ui = UI()
ui.window.mainloop()
