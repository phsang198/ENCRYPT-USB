from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import * 
from PyQt5.uic import loadUi

import sys
from PyQt5.QtCore import Qt , QTimer

import os
import sys
import psutil
import subprocess
import hashlib

filesystem = []
devicename = []


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        uic.loadUi('new.ui',self)
        self.setWindowTitle("USB encrypt")
        self.setFixedHeight(363)
        self.setFixedWidth(355)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint) 
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.show()

        self.ui_conttrol()

    def ui_conttrol(self):
        self.tab_encrypt.clicked.connect(lambda: self.changePage(0))
        self.tab_update.clicked.connect(lambda: self.changePage(1))
        self.tab_delete.clicked.connect(lambda: self.changePage(2))
        self.tab_decrypt.clicked.connect(lambda: self.changePage(3))

        self.btnEncrypt.clicked.connect(self.encrypt)
        self.btnUpdate.clicked.connect(self.update)
        self.btnDelete.clicked.connect(self.delete)
        self.btnDecrypt.clicked.connect(self.decrypt_usb)
        
        device = self.list_usb_drives()
        for i in device:
            self.comboBox.addItem(i)

    #################################################################################
    def changePage(self, index):
        self.stackedWidget.setCurrentIndex(index)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def list_usb_drives(self):
        usb_drives = []

        for partition in psutil.disk_partitions():
            if "removable" in partition.opts or "cdrom" in partition.opts:
                usb_drives.append(partition.device)

        return usb_drives
    #################################################################################
    def encrypt(self):
        if self.comboBox.currentIndex() == 0: 
            return
        if not self.key.text():
            self.showMessageBox('Error','pls input key')
            return
        if not self.confirm.text():
            self.showMessageBox('Error','pls input confirm key')
            return
        if self.key.text() != self.confirm.text() :
            self.showMessageBox('Error','key and confirm key not match')
            return 
        
        self.btnEncrypt.enable = False
        _driver = self.comboBox.currentText() 

        commands = 'manage-bde -lock ' + _driver[0] + ': -forcedismount'
        command_with_password = f'echo {self.confirm.text()} | {commands}'

        try:
            subprocess.run(command_with_password, shell=True, check=True)
        except Exception as e:
            print(f"Lệnh thực hiện không thành công. Mã lỗi: {e.returncode}")
            self.showMessageBox('Error',str(e))
            self.btnEncrypt.enable = True
            return

        self.encrypt_usb(_driver, self.confirm.text())
        
        with open('C:/password.txt', "wb") as f:
            password = self.confirm.text().encode('utf-8')
            f.write(password)

        self.showMessageBox('MSG','Eecrypt successfully!')
    #################################################################################
    def update(self):
        if self.comboBox.currentIndex() == 0: 
            return
        if not self.uexkey.text():
            self.showMessageBox('Error','pls input exist key')
            return
        if not self.ukey.text():
            self.showMessageBox('Error','pls input new key')
            return
        if not self.uconfirm.text():
            self.showMessageBox('Error','pls input confirm key')
            return
        if self.ukey.text() != self.uconfirm.text() :
            self.showMessageBox('Error','new key and confirm key not match')
            return 
        
        _driver = self.comboBox.currentText() 

        commands = 'manage-bde -changekey ' + _driver[0] + ': -forcedismount'
        command_with_password = f'echo {self.uconfirm.text()} | {commands}'

        try:
            subprocess.run(command_with_password, shell=True, check=True)
        except Exception as e:
            print(f"Lệnh thực hiện không thành công. Mã lỗi: {e.returncode}")
            self.showMessageBox('Error',str(e))
            return

        self.showMessageBox('MSG','Update key successfully!')
    #################################################################################
    def delete(self):
        if self.comboBox.currentIndex() == 0: 
            return
        if not self.dexkey.text():
            self.showMessageBox('Error','pls input exist key')
            return
       
        _driver = self.comboBox.currentText() 

        commands = 'manage-bde -unlock ' + _driver[0] + ': -forcedismount'
        command_with_password = f'echo {self.dexkey.text()} | {commands}'

        try:
            subprocess.run(command_with_password, shell=True, check=True)
        except Exception as e:
            print(f"Lệnh thực hiện không thành công. Mã lỗi: {e.returncode}")
            self.showMessageBox('Error',str(e))
            return

        self.showMessageBox('MSG','Delete key successfully!')
        self.decrypt_usb()
    #################################################################################
    def decrypt_usb(self):
        if self.comboBox.currentIndex() == 0: 
            return
        if not self.txtdecrypt.text():
            self.showMessageBox('Error','pls input key')
            return
        
        save_pass = open("C:/password.txt", "r").read()

        if self.txtdecrypt.text() != save_pass :
            self.showMessageBox('Error','invalid key')
            return 
        
        driver = self.comboBox.currentText() 

        file_list = self.get_file_list(driver)
        for file_path in file_list:
            self.decrypt_file(file_path, self.txtdecrypt.text())

        self.showMessageBox('MSG','Decrypt successfully!')
    #################################################################################
    def encrypt_usb(self,driver,password):
        file_list = self.get_file_list(driver)
        for file_path in file_list:
            self.set_password(file_path, password)

    def get_file_list(self,path):
        file_list = []
        for root, dirs, files in os.walk(path):
            for file in files:
                file_list.append(os.path.join(root, file))
        return file_list
    #################################################################################
    def decrypt_file(self,file_path, password):
        pas_len = len(password)
        count = 0
        new = b"" 

        with open(file_path, "rb") as f:
            encrypted_data = f.read()

        for i in encrypted_data:
            if count == pas_len:
                count = 0
            new += bytes([i ^ ord(password[count])])  
            count += 1

        with open(file_path, "wb") as f:
            f.write(new)

    #################################################################################
    def set_password(self, file_path, password):
        pas_len = len(password)
        count = 0
        new = b""  # Initialize new as bytes

        with open(file_path, "rb") as f:
            current = f.read()

        for i in current:
            if count == pas_len:
                count = 0
            new += bytes([i ^ ord(password[count])])  # Use bytes() to create a bytes object
            count += 1

        with open(file_path, "wb") as f:
            f.write(new)
    #################################################################################   
    def showMessageBox(self,info,text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle(info)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()

    sys.exit(app.exec())
