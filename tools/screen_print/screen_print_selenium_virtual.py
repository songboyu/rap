#-*-coding:utf-8-*-
import time

from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.common.exceptions import TimeoutException

class Pagescreen():
    def __init__(self):
        self.display = Display(visible=0, size=(1200, 900))
        self.display.start()

        self.driver = webdriver.Firefox() # Get local session of firefox
        self.driver.set_window_size(800, 600)
        self.driver.set_page_load_timeout(60)

    def capture(self, url, save_fn="capture.png"):
        try:
            self.driver.get(url)
            time.sleep(1)
            self.driver.get_screenshot_as_file(save_fn)
            print u'【save OK】: '+save_fn
            print

            return True
        except TimeoutException:  
            print 'time out after 30 seconds when loading page'
            print  
            self.driver.execute_script('window.stop()') #当页面加载时间超过设定时间，通过执行Javascript来stop加载，即可执行后续动作
            return False

    def quit():
        self.driver.quit()
        