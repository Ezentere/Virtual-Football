from threading import Thread, Lock, Event
from time import sleep, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException
from selenium.webdriver.chrome.service import Service as ChromeService
from subprocess import CREATE_NO_WINDOW
import schedule, os, sys
import pandas as pd
from win10toast import ToastNotifier

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
        self._kill = Event()
        self.toast = ToastNotifier()
        self.url = url
        self.username = username
        self.password = password
        self.browserProfile = webdriver.ChromeOptions()
        self.browserProfile.add_experimental_option('prefs', {'intl.accept_languages':'en,en_US'})
        self.browserProfile.add_argument('--window-size=1920,1080')
        self.browserProfile.add_argument('--log-level=2')
        self.browserProfile.add_argument("--headless") 
        self.chrome_service = ChromeService('chromedriver')
        self.chrome_service.creationflags = CREATE_NO_WINDOW

        schedule.every(30).seconds.do(self.bot)

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
                try: 
                    df.to_excel(f"{desktop}/sanalfutbol.xlsx", sheet_name='SANAL', encoding='utf-8', index=False)
                    self.toast.show_toast(
                        "Virtual Football",
                        "Excel dosyası desktop'a kopyalandı.",
                        duration = 20,
                        icon_path = "images/favicon.ico",
                        threaded = True,
                    )
                except PermissionError:
                    self.toast.show_toast(
                        "Virtual Football",
                        "Excel dosyası açtık durumda olduğu için işlem gerçekleştirilemedi.",
                        duration = 20,
                        icon_path = "images/favicon.ico",
                        threaded = True,
                    )


        self.browser.quit()

    def checkGet(self):
        permission = False
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
                hafta = self.browser.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]").text.split(' ')[1]
                break
            except:
                pass
        
        if hafta == "30":
            while True:
                is_killed = self._kill.wait(0.05)
                if is_killed:
                    sys.exit()
                try:
                    period = self.browser.find_element_by_xpath("/html/body/div[1]/div[5]/div/div[3]").text
                    break
                except:
                    pass
            self.browser.switch_to.default_content()
            if period == "Devre Arası" or \
               period == "İkinci Yarı" or \
               period == "Maç haftası sonu" or \
               period == "Maç sonu":
                permission = self.get()
        return permission

    def get(self):
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
            while True:
                is_killed = self._kill.wait(0.05)
                if is_killed:
                    sys.exit()
                try:
                    haftabutton = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[3]/div/ul/li[{j}]")
                    haftabutton.click()
                    is_killed = self._kill.wait(0.25)
                    if is_killed:
                        sys.exit()
                    break
                except:
                    pass

            macListesi = []
            sayac = 0
            while True:
                sayac += 1
                print(f"sayac: {sayac}")
                is_killed = self._kill.wait(0.05)
                if is_killed:
                    sys.exit()
                try:
                    if sayac > 3 and j == 1:
                        self.browser.refresh()
                        is_killed = self._kill.wait(2)
                        if is_killed:
                            sys.exit()
                        sayac = 0
                    macListesi = self.browser.find_elements_by_xpath("/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li")
                    is_killed = self._kill.wait(0.05)
                    if is_killed:
                        sys.exit()
                    if len(macListesi) == 8:
                        is_killed = self._kill.wait(0.1)
                        if is_killed:
                            sys.exit()
                        break
                except:
                    continue

            while True:
                try:
                    btn = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[8]/div[1]/div/a[1]")
                    btn.click()
                    is_killed = self._kill.wait(0.75)
                    if is_killed:
                        sys.exit()
                    break
                except:
                    pass

            for i in range(1, len(macListesi)):
                while True:
                    try:
                        mac = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]")
                        self.browser.execute_script("arguments[0].style.display = 'block';", mac)
                        sleep(0.01)
                        break
                    except:
                        pass

            for i in range(1, len(macListesi)+1):
                ai = 0
                while True:
                    ai = ai + 1
                    print(f"ai: {ai}")
                    try:
                        mac_ismi = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[1]/ul/li/div/div/div[1]")
                        ms1 = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[1]/ul/li/div/div/div[2]/div[1]/a/span")
                        ms0 = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[1]/ul/li/div/div/div[2]/div[2]/a/span")
                        ms2 = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[1]/ul/li/div/div/div[2]/div[3]/a/span")
                        iy1 = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[2]/ul/li/ul/li/div[2]/div/div[2]/div[1]/a/span")
                        iy0 = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[2]/ul/li/ul/li/div[2]/div/div[2]/div[2]/a/span")
                        iy2 = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[2]/ul/li/ul/li/div[2]/div/div[2]/div[3]/a/span")
                        altust1 = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[1]/div[1]/li[1]/span")
                        birust = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[1]/div[1]/li[2]/div/a/span")
                        biralt = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[1]/div[2]/li[2]/div/a/span")
                        ikiust = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[2]/div[1]/li[2]/div/a/span")
                        ikialt = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[2]/div[2]/li[2]/div/a/span")
                        ucust = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[3]/div[1]/li[2]/div/a/span")
                        ucalt = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[6]/ul/li/ul/li/div[2]/ul[3]/div[2]/li[2]/div/a/span")
                        ilk1 = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[4]/ul/li/ul/li/div/div[1]/div[2]/div/a/span")
                        ilk2 = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[4]/ul/li/ul/li/div/div[2]/div[2]/div/a/span")
                        ilk0 = self.browser.find_element_by_xpath(f"/html/body/div[7]/div[1]/div[4]/div/span/div/ul/li[{i}]/div[2]/div/ul/li[4]/ul/li/ul/li/div/div[3]/div[2]/div/a/span")
                        
                        break
                    except NoSuchElementException as e:
                        print("Hata", e)
                
                ev_sahibi = mac_ismi.text.split(" ")[1]
                deplasman = mac_ismi.text.split(" ")[-1]
                
                ms1 = ms1.text
                ms0 = ms0.text
                ms2 = ms2.text
                iy1 = iy1.text
                iy0 = iy0.text
                iy2 = iy2.text

                if altust1.text == "0.5":
                    altust05ust = birust.text
                    altust05alt = biralt.text
                    altust15ust = ikiust.text
                    altust15alt = ikialt.text
                    altust25ust = ucust.text
                    altust25alt = ucalt.text
                    altust35ust = ""
                    altust35alt = ""
                    altust45ust = ""
                    altust45alt = ""
                    
                if altust1.text == "1.5":
                    altust05ust = ""
                    altust05alt = ""
                    altust15ust = birust.text
                    altust15alt = biralt.text
                    altust25ust = ikiust.text
                    altust25alt = ikialt.text
                    altust35ust = ucust.text
                    altust35alt = ucalt.text
                    altust45ust = ""
                    altust45alt = ""
                    
                if altust1.text == "2.5":
                    altust05ust = ""
                    altust05alt = ""
                    altust15ust = ""
                    altust15alt = ""
                    altust25ust = birust.text
                    altust25alt = biralt.text
                    altust35ust = ikiust.text
                    altust35alt = ikialt.text
                    altust45ust = ucust.text
                    altust45alt = ucalt.text
                
                ilk0 = ilk0.text
                ilk1 = ilk1.text
                ilk2 = ilk2.text

                self.data.append([f"{i}.Maç",j,sezon,ev_sahibi,deplasman,ms1,ms0,ms2,iy1,iy0,iy2,altust05ust,altust05alt,altust15ust,altust15alt,altust25ust,altust25alt,altust35ust,altust35alt,altust45ust,altust45alt,ilk1,ilk2,ilk0])

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
                schedule.run_pending()
                is_killed = self._kill.wait(1)
                if is_killed:
                    sys.exit()
        try:
            if self.stopped:
                self.browser.quit()
        except:
            print("Stop")
