# ADB Python Client
### 　Use ADB to upload/download SMALL files to/from your Android Device without USB

## Usage
```
python main.py
```

1. PC and Android device must in the same LAN.

2. Make sure you can use "adb connect <Android IP>" to connect to your device.

　　Maybe you should open developer mode / root your device / install an ADB Apps (such as "WiFi ADB")

3. Input <Android IP> in the left-top box and press "Connect"

4. Instructions are in the picture below.

## Attention

1. Python package: adb_shell will open only 1 session for a device at a time and 

　　UPLOAD/DOWNLOAD CANNOT GOES ASYNCHRONOUSLY easily.

