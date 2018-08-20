from selenium import webdriver
from selenium.webdriver.common.keys import Keys


CHROME_DRIVER_PATH = "chromedriver.exe"
FIREFOX_DRIVER_PATH = "geckodriver.exe"


class Driver():

    def __init__(self, driver_exe_path):
        self.driver = webdriver.Firefox()
        #webdriver.Chrome(driver_exe_path)

if __name__ == "__main__":
    test_driver = Driver(CHROME_DRIVER_PATH)
