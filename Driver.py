from threading import Thread, Lock, Event
from time import sleep, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException
from selenium.webdriver.chrome.service import Service as ChromeService
from subprocess import CREATE_NO_WINDOW
import os, sys
import pandas as pd
from win10toast import ToastNotifier
from bs4 import BeautifulSoup as BS
from lxml import etree
import requests

class ChromeDriver:

    stopped = True
    lock = None
    t = None

    browser = None
    browserProfile = None

    url = ""
    username = ""
    password = ""
    path = ""
    errorMessageState = False
    errorMessage = ""
    data = []
    firstStart = True
    botStatus = False

    def __init__(self, url, username, password, path):
        self.lock = Lock()
        self._kill = Event()
        self.toast = ToastNotifier()
        self.url = url
        self.username = username
        self.password = password
        self.path = path
        self.browserProfile = webdriver.ChromeOptions()
        self.browserProfile.add_experimental_option('prefs', {'intl.accept_languages':'en,en_US'})
        self.browserProfile.add_argument('--window-size=1920,1080')
        self.browserProfile.add_argument('--log-level=2')
        self.browserProfile.add_argument("--headless") 
        self.chrome_service = ChromeService('chromedriver')
        self.chrome_service.creationflags = CREATE_NO_WINDOW

    def resetSelfs(self):
        self.lock.acquire()
        self.errorMessageState = False
        self.lock.release()

    def login(self):
        self.browser.get(f'https://{self.url}.com')
        is_killed = self._kill.wait(0.075)
        if is_killed:
            sys.exit()
        while True:
            is_killed = self._kill.wait(0.1)
            if is_killed:
                sys.exit()
            try:
                pb_Login = self.browser.find_element_by_class_name("coupon-link.login-link")
                pb_Login.click()
                break
            except NoSuchElementException:
                continue
        while True:
            is_killed = self._kill.wait(0.1)
            if is_killed:
                sys.exit()
            try:
                usrname_bar = self.browser.find_element_by_name('username')
                passwrd_bar = self.browser.find_element_by_name('password')
                break
            except NoSuchElementException:
                continue

        usrname_bar.send_keys(self.username)
        passwrd_bar.send_keys(self.password + Keys.ENTER)
        is_killed = self._kill.wait(1)
        if is_killed:
            sys.exit()

        try:
            alert = self.browser.switch_to.alert
            print(alert.text)
            alert.accept()
            elementExist = "errorPass"
        except NoAlertPresentException:
            elementExist = "notError"

        return elementExist

    def bot(self):
        self.browser = webdriver.Chrome("chromedriver.exe", chrome_options=self.browserProfile, service=self.chrome_service)
        is_killed = self._kill.wait(0.025)
        if is_killed:
            sys.exit()
        permission = False

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
            permission = self.get()

        self.browser.quit()

        if permission:
            df = pd.DataFrame(self.data, columns=["Lig","Hafta","Sezon","Ev Sahibi","Misafir","1","X","2","IY 1","IY 0","IY 2","0,5 ALT","0,5 ALT","1,5 ÜST","1,5 ALT","2,5 ÜST","2,5 ALT","3,5 ÜST","3,5 ALT","4,5 ÜST","4,5 ALT","İLK-1","İLK-2","İLK HİÇBİRİ"])
            print(df)
            if self.path == "":
                desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            else:
                desktop = self.path
            while True:
                try: 
                    df.to_excel(f"{desktop}/{self.data[0][2]}_Oranlar.xlsx", sheet_name='SANAL', encoding='utf-8', index=False)
                    self.toast.show_toast(
                        "Virtual Football",
                        "Excel dosyası desktop'a kopyalandı.",
                        duration = 45,
                        icon_path = "images/favicon.ico",
                        threaded = True,
                    )
                    break
                except PermissionError:
                    self.toast.show_toast(
                        "Virtual Football",
                        "Excel dosyası açtık durumda olduğu için işlem gerçekleştirilemedi.\nLütfen excel dosyasını kapatınız.",
                        duration = 30,
                        icon_path = "images/favicon.ico",
                        threaded = True,
                    )
                    sleep(5)
            self.data.clear()
        self.botStatus = False

    def checkGet(self):
        self.browser = webdriver.Chrome("chromedriver.exe", chrome_options=self.browserProfile, service=self.chrome_service)
        is_killed = self._kill.wait(0.025)
        if is_killed:
            sys.exit()
        self.browser.get('https://rgs.betradar.com/vflyouwinrgs/vleague.php?clientid=594&lang=tr&style=newbetboo')
        is_killed = self._kill.wait(3)
        if is_killed:
            sys.exit()
        i = 0
        while True:
            is_killed = self._kill.wait(0.05)
            if is_killed:
                sys.exit()
            try:
                sezon = self.browser.find_element_by_xpath('//*[@id="tab_season"]').text.split(" ")[1]
                hafta = self.browser.find_element_by_xpath('//*[@id="tab_matchday"]').text.split(' ')[1]
                period = self.browser.find_element_by_xpath('//*[@id="period"]').text
                break
            except Exception as e:
                print(e)
                if i == 5:
                    with open("log.txt", "a") as file:
                        file.write(f"\n\n\n{e}\n\n\n")
                    break
                i += 1
        
        print(f"{sezon}-{hafta}: {period}")
        with open("log.txt", "a") as file:
            file.write(f"{sezon}-{hafta}: {period}\n")

        if period == "Sezon başı":
            self.botStatus = True
        
        self.browser.quit()

    def get(self):
        as_ = time()
        self.browser.get(f'https://{self.url}.com/sanalfutbol.php')
        
        is_killed = self._kill.wait(3)
        if is_killed:
            sys.exit()
        
        while True:
            is_killed = self._kill.wait(0.05)
            if is_killed:
                sys.exit()
            try:
                self.browser.switch_to.frame(self.browser.find_element_by_tag_name("iframe"))
                sezon = self.browser.find_element_by_xpath("html/body/div[1]/div[2]/div[1]").text.split(' ')[1]
                self.browser.switch_to.default_content()
                break
            except NoSuchElementException:
                continue

        while True:
            is_killed = self._kill.wait(0.05)
            if is_killed:
                sys.exit()
            try:
                hafta = self.browser.find_element_by_class_name("onhafta").text
                break
            except NoSuchElementException:
                continue
        
        for j in range(int(hafta), 31):
            request_cookies_browser = self.browser.get_cookies()
            params = {'hid':j, 'oid':'macsonucu'}
            s = requests.Session()
            c = [s.cookies.set(c['name'], c['value']) for c in request_cookies_browser]
            resp = s.post(f"https://{self.url}.com/sbAjaxS.php?a=oranlar&odetay={j}", params)
            soup = BS(resp.content, 'html.parser')
            dom = etree.HTML(str(soup))
            macListesi = dom.xpath('//*[@id="marketContainer"]/li')
            for i in range(1, len(macListesi)+1):
                try:
                    mac_ismi = dom.xpath(f'//*[@id="marketContainer"]/li[{i}]/div[1]/ul/li/div/div/div[1]')[0].text.strip()
                    ms1 = dom.xpath(f'//*[@id="marketContainer"]/li[{i}]/div[1]/ul/li/div/div/div[2]/div[1]/a/span')[0].text.strip()
                    ms0 = dom.xpath(f'//*[@id="marketContainer"]/li[{i}]/div[1]/ul/li/div/div/div[2]/div[2]/a/span')[0].text.strip()
                    ms2 = dom.xpath(f'//*[@id="marketContainer"]/li[{i}]/div[1]/ul/li/div/div/div[2]/div[3]/a/span')[0].text.strip()
                    iy1 = dom.xpath(f'//*[@id="marketContainer"]/li[{i}]/div[2]/div/ul/li[2]/ul/li/ul/li/div[2]/div/div[2]/div[1]/a/span')[0].text.strip()
                    iy0 = dom.xpath(f'//*[@id="marketContainer"]/li[{i}]/div[2]/div/ul/li[2]/ul/li/ul/li/div[2]/div/div[2]/div[2]/a/span')[0].text.strip()
                    iy2 = dom.xpath(f'//*[@id="marketContainer"]/li[{i}]/div[2]/div/ul/li[2]/ul/li/ul/li/div[2]/div/div[2]/div[3]/a/span')[0].text.strip()
                    ilk1 = dom.xpath(f'//*[@id="marketContainer"]/li[{i}]/div[2]/div/ul/li[4]/ul/li/ul/li/div/div[1]/div[2]/div/a/span')[0].text.strip()
                    ilk0 = dom.xpath(f'//*[@id="marketContainer"]/li[{i}]/div[2]/div/ul/li[4]/ul/li/ul/li/div/div[3]/div[2]/div/a/span')[0].text.strip()
                    ilk2 = dom.xpath(f'//*[@id="marketContainer"]/li[{i}]/div[2]/div/ul/li[4]/ul/li/ul/li/div/div[2]/div[2]/div/a/span')[0].text.strip()
                    altust1 = dom.xpath(f'//*[@id="marketContainer"]/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[1]/div[1]/li[1]/span')[0].text.strip()
                    birust = dom.xpath(f'//*[@id="marketContainer"]/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[1]/div[1]/li[2]/div/a/span')[0].text.strip()
                    biralt = dom.xpath(f'//*[@id="marketContainer"]/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[1]/div[2]/li[2]/div/a/span')[0].text.strip()
                    ikiust = dom.xpath(f'//*[@id="marketContainer"]/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[2]/div[1]/li[2]/div/a/span')[0].text.strip()
                    ikialt = dom.xpath(f'//*[@id="marketContainer"]/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[2]/div[2]/li[2]/div/a/span')[0].text.strip()
                    ucust = dom.xpath(f'//*[@id="marketContainer"]/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[3]/div[1]/li[2]/div/a/span')[0].text.strip()
                    ucalt = dom.xpath(f'//*[@id="marketContainer"]/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[3]/div[2]/li[2]/div/a/span')[0].text.strip()
                    ev_sahibi = mac_ismi.split(" ")[1]
                    deplasman = mac_ismi.split(" ")[-1]
                    if altust1 == "0.5":
                        altust05ust = birust
                        altust05alt = biralt
                        altust15ust = ikiust
                        altust15alt = ikialt
                        altust25ust = ucust
                        altust25alt = ucalt
                        altust35ust = ""
                        altust35alt = ""
                        altust45ust = ""
                        altust45alt = ""
                        
                    if altust1 == "1.5":
                        altust05ust = ""
                        altust05alt = ""
                        altust15ust = birust
                        altust15alt = biralt
                        altust25ust = ikiust
                        altust25alt = ikialt
                        altust35ust = ucust
                        altust35alt = ucalt
                        altust45ust = ""
                        altust45alt = ""
                        
                    if altust1 == "2.5":
                        altust05ust = ""
                        altust05alt = ""
                        altust15ust = ""
                        altust15alt = ""
                        altust25ust = birust
                        altust25alt = biralt
                        altust35ust = ikiust
                        altust35alt = ikialt
                        altust45ust = ucust
                        altust45alt = ucalt
                except:
                    pass

                self.data.append([f"{i}.Maç",j,sezon,ev_sahibi,deplasman,ms1,ms0,ms2,iy1,iy0,iy2,altust05ust,altust05alt,altust15ust,altust15alt,altust25ust,altust25alt,altust35ust,altust35alt,altust45ust,altust45alt,ilk1,ilk2,ilk0])

        print(f"{sezon}-{hafta} oranları {time()-as_} saniye içinde yazıldı.")
        with open("log.txt", "a") as file:
            file.write(f"{sezon}-{hafta} oranları {time()-as_} saniye içinde yazıldı.\n")
        return True

    def start(self):
        self.stopped = False
        self.t = Thread(target=self.run)
        self.t.start()
    
    def stop(self):
        self.stopped = True
        self.kill()
        self.t.join()

    def alive(self):
        return self.t.isAlive()

    def kill(self):
        self._kill.set()

    def run(self):
        while not self.stopped:
            if self.firstStart:
                sa = time()
                self.bot()
                print(time()-sa)
                self.firstStart = False
            else:
                if self.botStatus:
                    self.bot()
                else:
                    self.checkGet()
                
            is_killed = self._kill.wait(2)
            if is_killed:
                sys.exit()
        try:
            if self.stopped:
                self.browser.quit()
        except:
            print("Stop")
