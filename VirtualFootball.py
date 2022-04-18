from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import json, os, shutil, keyboard
from time import sleep, time

from main import Ui_MainWindow
from AboutMe import Ui_mw_AboutMe
import images_rc

from Driver import ChromeDriver

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import webbrowser

class VirtualFootball(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.AboutMePage = QMainWindow()
        self.Abui = Ui_mw_AboutMe()
        self.Abui.setupUi(self.AboutMePage)

        self.SaveJson = "Settings.json"
        self.SaveDir = "./" + self.SaveJson
        self.JsonLayout = {}

        self.Load()
        self.ActionButton()

        self.timerCheckErrors = QTimer(self)
        self.timerCheckErrors.timeout.connect(self.checkErrors)

        self.timerCheckKeyboard = QTimer(self)
        self.timerCheckKeyboard.timeout.connect(self.checkKeyboard)

        self.Driver = None

    def GetAboutMePage(self):
        self.AboutMePage.show()

    def Load(self):
        self.ui.le_URL.setText("")
        self.ui.le_Username.setText("")
        self.ui.le_Password.setText("")
        
        if os.path.exists(self.SaveDir):
            with open(self.SaveDir,"r") as json_data:
                self.JsonLayout = json.load(json_data)

            if "Settings" in self.JsonLayout:
                if "URL" in self.JsonLayout["Settings"]:
                    self.ui.le_URL.setText(self.JsonLayout["Settings"]["URL"])
                if "Username" in self.JsonLayout["Settings"]:
                    self.ui.le_Username.setText(self.JsonLayout["Settings"]["Username"])
                if "Password" in self.JsonLayout["Settings"]:
                    self.ui.le_Password.setText(self.JsonLayout["Settings"]["Password"])

    def Save(self):
        self.JsonLayout.clear()
        self.JsonLayout["Settings"] = {}
        if self.ui.le_URL.text() != "":
            URL = self.ui.le_URL.text()
            self.JsonLayout["Settings"]["URL"] = URL
        if self.ui.le_Password.text() != "":
            Password = self.ui.le_Password.text()
            self.JsonLayout["Settings"]["Password"] = Password
        if self.ui.le_Username.text() != "":
            Username = self.ui.le_Username.text()
            self.JsonLayout["Settings"]["Username"] = Username
        with open(self.SaveDir, "w") as json_data:
            json.dump(self.JsonLayout, json_data)

    def ActionButton(self):
        button_action = QAction("Hakkımda", self)
        button_action.triggered.connect(self.GetAboutMePage)
        self.ui.toolBar.addAction(button_action)

        self.ui.le_URL.textChanged.connect(self.Save)
        self.ui.le_Username.textChanged.connect(self.Save)
        self.ui.le_Password.textChanged.connect(self.Save)
        self.ui.pb_Start.clicked.connect(self.Start)

        self.Abui.label.mousePressEvent = self.goLink

    def goLink(self, event):
        chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
        webbrowser.get(chrome_path).open('https://github.com/Ezentere')
            
    def CreateMessageBox(self, message, buttons=(QMessageBox.Ok | QMessageBox.Cancel)):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("UYARI")
        msg.setStandardButtons(buttons)
        retval = msg.exec_()
        return retval

    def checkErrors(self):
        if self.Driver.errorMessageState:
            self.show()
            self.Stop()
            errorMessage = self.Driver.errorMessage
            self.Driver.resetSelfs()
            sleep(0.05)
            self.CreateMessageBox(errorMessage, QMessageBox.Ok)

    def checkKeyboard(self):
        if keyboard.is_pressed('ctrl+shift+q'):
            self.show()
            self.Stop()

    def Start(self):
        self.Save()
        url = self.ui.le_URL.text()
        username = self.ui.le_Username.text()
        password = self.ui.le_Password.text()
        if url != "" and username != "" and password != "":
            if url.find("/") == -1 and url.find(".") == -1:
                retval = self.CreateMessageBox("Bot çalışmaya başlıyor...\nDevam etmek istiyor musunuz?\nBotu durdurmak için 'ctrl+shift+q' kombinasyonunu kullanınız...")
                if retval == QMessageBox.Ok:
                    self.Driver = ChromeDriver(url, username, password)
                    self.Driver.start()
                    self.timerCheckErrors.start(100)
                    self.timerCheckKeyboard.start(10)
                    self.hide()
            else:
                self.CreateMessageBox("Geçersiz URL", QMessageBox.Ok)
        else:
            self.CreateMessageBox("Tüm alanları doldurunuz.", QMessageBox.Ok)

    def Stop(self):
        self.timerCheckErrors.stop()
        try:
            self.Driver.stop()
        except:
            pass
        
    def closeEvent(self, event):
        if self.AboutMePage.isVisible():
            self.AboutMePage.close()
        self.Stop()

def main():

	### BURADA __pycache__ klasörü temizleniyor.
	path = './'
	for directories, subfolder, files in os.walk(path):
		if os.path.isdir(directories):
			if directories[::-1][:11][::-1] == '__pycache__':
							shutil.rmtree(directories)

	app = QApplication([])
	app.setStyle("Vista")
	ui = VirtualFootball()
	ui.show()
	app.exec_()

if __name__ == '__main__':
    main()