from threading import Thread, Lock
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException
from time import sleep
import schedule, os
import pandas as pd
class ChromeDriver:

    stopped = True
    lock = None
    t = None

    browser = None
    browserProfile = None

    url = ""
    username = ""
    password = ""
    errorMessageState = False
    errorMessage = ""
    data = []
    firstStart = True

    def __init__(self, url, username, password):
        self.lock = Lock()
        self.url = url
        self.username = username
        self.password = password
        self.browserProfile = webdriver.ChromeOptions()
        self.browserProfile.add_experimental_option('prefs', {'intl.accept_languages':'en,en_US'})
        self.browserProfile.add_argument('--window-size=1920,1080')
        self.browserProfile.add_argument('--log-level=2')
        self.browserProfile.add_argument("--headless") 

        schedule.every(2).minutes.do(self.bot)

    def resetSelfs(self):
        self.lock.acquire()
        self.errorMessageState = False
        self.lock.release()

    def login(self):
        self.browser.get(f'https://{self.url}.com')
        sleep(0.075)
        while True:
            sleep(0.1)
            try:
                pb_Login = self.browser.find_element_by_class_name("coupon-link.login-link")
                pb_Login.click()
                break
            except NoSuchElementException:
                continue
        while True:
            sleep(0.1)
            try:
                usrname_bar = self.browser.find_element_by_name('username')
                passwrd_bar = self.browser.find_element_by_name('password')
                break
            except NoSuchElementException:
                continue

        usrname_bar.send_keys(self.username)
        passwrd_bar.send_keys(self.password + Keys.ENTER)
        sleep(1)

        try:
            alert = self.browser.switch_to.alert
            print(alert.text)
            alert.accept()
            elementExist = "errorPass"
        except NoAlertPresentException:
            elementExist = "notError"

        return elementExist

    def bot(self):
        print("başladı.")
        self.browser = webdriver.Chrome("chromedriver.exe", chrome_options=self.browserProfile)
        sleep(0.025)
        
        while True:
            loginError = self.login()
            if loginError == "errorPass":
                self.browser.quit()
                self.lock.acquire()
                self.errorMessageState = True
                self.errorMessage = "Kullanıcı adı veya şifre hatalı..."
                self.lock.release()
            else:
                break

        if loginError == "notError":
            permission = False
            if self.firstStart:
                permission = self.get()
            else:
                permission = self.checkGet()
            
            if permission:
                df = pd.DataFrame(self.data, columns=["Lig","Hafta","Sezon","Ev Sahibi","Misafir","1","X","2","IY 1","IY 0","IY 2","0,5 ALT","0,5 ALT","1,5 ÜST","1,5 ALT","2,5 ÜST","2,5 ALT","3,5 ÜST","3,5 ALT","4,5 ÜST","4,5 ALT","İLK-1","İLK-2","İLK HİÇBİRİ"])
                print(df)
                desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
                df.to_excel(f"{desktop}/sanalfutbol.xlsx", sheet_name='SANAL', encoding='utf-8', index=False)

        self.browser.quit()

    def checkGet(self):
        print("checkGet")
        permission = False
        self.browser.get(f'https://{self.url}.com/sanalfutbol.php')
        sleep(3)
        while True:
            sleep(0.05)
            try:
                hafta = self.browser.find_element_by_class_name("onhafta").text
                if hafta == "1":
                    permission = self.get()
                break
            except NoSuchElementException:
                continue
        
        return permission

    def get(self):
        self.browser.get(f'https://{self.url}.com/sanalfutbol.php')
        
        sleep(3)

        while True:
            sleep(0.05)
            try:
                self.browser.switch_to.frame(self.browser.find_element_by_tag_name("iframe"))
                sezon = self.browser.find_element_by_xpath("html/body/div[1]/div[2]/div[1]").text.split(' ')[1]
                gamestatus = self.browser.find_element_by_xpath("/html/body/div[1]/div[5]/div/div[3]").text
                self.browser.switch_to.default_content()
                break
            except NoSuchElementException:
                continue

        while True:
            sleep(0.05)
            try:
                hafta = self.browser.find_element_by_class_name("onhafta").text
                break
            except NoSuchElementException:
                continue

        if gamestatus == "İkinci Yarı":
            hafta = str(int(hafta) + 1)
            while True:
                sleep(0.05)
                try:
                    haftabutton = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[3]/div/ul/li[{hafta}]")
                    haftabutton.click()
                    sleep(1.35)
                    break
                except NoSuchElementException:
                    continue

        for j in range(int(hafta), 31):
            while True:
                sleep(0.05)
                try:
                    haftabutton = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[3]/div/ul/li[{j}]")
                    haftabutton.click()
                    sleep(1.35)
                    break
                except NoSuchElementException:
                    continue

            macListesi = []
            while True:
                sleep(0.05)
                try:
                    macListesi = self.browser.find_elements_by_xpath("/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li")
                    sleep(0.1)
                    if len(macListesi) == 8:
                        sleep(0.5)
                        break
                except:
                    continue

            for i in range(1, len(macListesi)+1):
                self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[1]/div/a[1]").click()
                sleep(0.8)
                mac_ismi = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[1]/ul/li/div/div/div[1]").text
                ev_sahibi = mac_ismi.split(" ")[1]
                deplasman = mac_ismi.split(" ")[-1]
                ms1 = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[1]/ul/li/div/div/div[2]/div[1]/a/span").text
                ms0 = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[1]/ul/li/div/div/div[2]/div[2]/a/span").text
                ms2 = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[1]/ul/li/div/div/div[2]/div[3]/a/span").text
                iy1 = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[2]/ul/li/ul/li/div[2]/div/div[2]/div[1]/a/span").text
                iy0 = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[2]/ul/li/ul/li/div[2]/div/div[2]/div[2]/a/span").text
                iy2 = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[2]/ul/li/ul/li/div[2]/div/div[2]/div[3]/a/span").text
                
                altust1 = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[1]/div[1]/li[1]/span").text
                if altust1 == "0.5":
                    altust05ust = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[1]/div[1]/li[2]/div/a/span").text
                    altust05alt = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[1]/div[2]/li[2]/div/a/span").text
                    altust15ust = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[2]/div[1]/li[2]/div/a/span").text
                    altust15alt = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[2]/div[2]/li[2]/div/a/span").text
                    altust25ust = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[3]/div[1]/li[2]/div/a/span").text
                    altust25alt = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[3]/div[2]/li[2]/div/a/span").text
                    altust35ust = ""
                    altust35alt = ""
                    altust45ust = ""
                    altust45alt = ""
                    
                if altust1 == "1.5":
                    altust05ust = ""
                    altust05alt = ""
                    altust15ust = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[1]/div[1]/li[2]/div/a/span").text
                    altust15alt = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[1]/div[2]/li[2]/div/a/span").text
                    altust25ust = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[2]/div[1]/li[2]/div/a/span").text
                    altust25alt = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[2]/div[2]/li[2]/div/a/span").text
                    altust35ust = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[3]/div[1]/li[2]/div/a/span").text
                    altust35alt = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[3]/div[2]/li[2]/div/a/span").text
                    altust45ust = ""
                    altust45alt = ""
                    
                if altust1 == "2.5":
                    altust05ust = ""
                    altust05alt = ""
                    altust15ust = ""
                    altust15alt = ""
                    altust25ust = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[1]/div[1]/li[2]/div/a/span").text
                    altust25alt = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[1]/div[2]/li[2]/div/a/span").text
                    altust35ust = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[2]/div[1]/li[2]/div/a/span").text
                    altust35alt = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[2]/div[2]/li[2]/div/a/span").text
                    altust45ust = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[3]/div[1]/li[2]/div/a/span").text
                    altust45alt = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[3]/div[2]/li[2]/div/a/span").text

                ilk1 = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[4]/ul/li/ul/li/div/div[1]/div[2]/div/a/span").text
                ilk2 = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[4]/ul/li/ul/li/div/div[2]/div[2]/div/a/span").text
                ilk0 = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[4]/ul/li/ul/li/div/div[3]/div[2]/div/a/span").text
                self.data.append([f"{i}.Maç",j,sezon,ev_sahibi,deplasman,ms1,ms0,ms2,iy1,iy0,iy2,altust05ust,altust05alt,altust15ust,altust15alt,altust25ust,altust25alt,altust35ust,altust35alt,altust45ust,altust45alt,ilk1,ilk2,ilk0])

        return True

    def start(self):
        self.stopped = False
        self.t = Thread(target=self.run)
        self.t.start()
    
    def stop(self):
        self.stopped = True
        self.t.join()

    def run(self):
        while not self.stopped:
            if self.firstStart:
                self.bot()
                self.firstStart = False
            else:
                schedule.run_pending()
                sleep(1)
        try:
            if self.stopped:
                self.browser.quit()
        except:
            print("Stop")
