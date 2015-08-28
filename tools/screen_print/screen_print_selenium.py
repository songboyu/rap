#-*-coding:utf-8-*-
import time
import sys
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
#reload(sys)
#sys.setdefaultencoding('utf-8')
class Pagescreen():
    def __init__(self,proxy = None, port = 8580):
        if proxy:
            profile = webdriver.FirefoxProfile()
            profile.set_preference('network.proxy.type', 1)
            profile.set_preference('network.proxy.http', proxy)
            profile.set_preference('network.proxy.http_port', port)
            profile.set_preference('network.proxy.ssl', proxy)
            profile.set_preference('network.proxy.ssl_port', port)
            profile.update_preferences()
            self.driver = webdriver.Firefox(profile)
        else:
            self.driver = webdriver.Firefox() # Get local session of firefox
        self.driver.set_window_size(800, 600)

    def exejs(self):
        jquery = open('jquery-2.1.1.js','r')
        redjs = open('red.js','r')
        try:
            jquery_all = jquery.read()
            redjs_all = redjs.read()
        finally:
            jquery.close()
            redjs.close()
        self.driver.execute_script(jquery_all)
        self.driver.execute_script(redjs_all)

    def google_search(self, str_word, reg):
        if self.openweb('http://www.google.com'):
            elem = self.driver.find_element_by_id('lst-ib')
            elem.send_keys(str_word)
            elem.send_keys(Keys.RETURN)
            time.sleep(3)
            self.exejs()
            for i in range(3):
                if self.driver.execute_script(u'return redblock_g("'+str_word+'", "'+reg+'");'):
                    self.savepng(str_word+str(i)+'.png')
                elem_next = self.driver.find_element_by_id('pnnext')
                elem_next.click()
                time.sleep(3)

    def websearch(self, url, str_list):
        if self.openweb(url):
            self.exejs()
            for str_word in str_list:
                self.driver.execute_script(u'redblock(\''+str_word+'\');')
            self.savepng()

    def openweb(self, url):
        try:
            self.driver.set_page_load_timeout(60)
            self.driver.get(url)
            time.sleep(1)
            return True
        except TimeoutException:  
            print 'time out after 30 seconds when loading page'
            self.driver.execute_script('window.stop()') #当页面加载时间超过设定时间，通过执行Javascript来stop加载，即可执行后续动作
            self.driver.close()
            return False

    def savepng(self, save_fn="capture.png"):
        try:
            self.driver.get_screenshot_as_file(save_fn)
            print '[save OK]: '+save_fn
            print '---------------------------'
        except Exception,e:
            print str(e)
            self.driver.quit()

    def quit(self):
        self.driver.quit()
    
    
    def capture(self, save_fn="capture.png"):
        try:
            self.driver.set_page_load_timeout(60)
            self.driver.get(self.url)
            time.sleep(1)
            self.driver.get_screenshot_as_file(save_fn)
            print '[save OK]: '+save_fn
            print '---------------------------'

            return True
        except TimeoutException:  
            print 'time out after 30 seconds when loading page'
            self.driver.execute_script('window.stop()') #当页面加载时间超过设定时间，通过执行Javascript来stop加载，即可执行后续动作
            return False
    
