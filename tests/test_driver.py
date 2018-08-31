from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

## Path to drivers for browser testing
CHROME_DRIVER_PATH = "chromedriver.exe"
FIREFOX_DRIVER_PATH = "geckodriver.exe"
WEBSITE_URL = "http://127.0.0.1:8080/publicbanking/"

## Path of set of card numbers and passwords for testing
LOGIN_TESTS_FILE = "login_tests.txt"

## HTML page IDs for testing
#LOGIN_SUBMIT_BUTTON_ID = "login_submit"
LOGIN_NUMBER_FIELD_ID = "card_number"
PASS_NUMBER_FIELD_ID = "card_password"
LOGOUT_SUBMIT_BUTTON_ID = "logout_submit_button"


class Driver():
    """
    Class which runs the automated web testing software and evaluates the success of these tests

    Attributes:
        loginInfo (list): List with elements of type (list) which consist 2 elements (card_number, & password)
    """
    loginInfo = []

    def __init__(self, driver_exe_path):
        self.driver = webdriver.Chrome()

        self.loadWebsite()
        self.enterLoginTests()

    def loadWebsite(self):
        """
        Function which loads a new browser window to the home page of application

        Returns:
            result (bool): Indicates if website loaded successfully
        """
        self.loadLoginFile(LOGIN_TESTS_FILE)
        self.driver.get(WEBSITE_URL)

        result = True
        return result

    def enterLoginTests(self):
        """
        Function which runs through each login test set, and evaluates the sucess of each test

        Returns:
            result (bool): Indicates if all login tests were performed successfully
        """
        i = 1
        for loginTest in self.loginInfo:
            print("Testing login set {}".format(i))
            i+=1
            self.loginWithInformation(loginTest[0], loginTest[1])
        print("Completed login tests")

        result = True
        return result

    def loginWithInformation(self, card, password):
        """
        Function which finds the card and password fields of the login page, and enters the arguments provided
        in the elements

        Args:
            card (str): Card Number for login purposes
            password (str): Password for account
        Returns:
            result (bool): Indicates if the information was entered successfully
            
        """
        try:
            cardField = self.driver.find_element_by_id(LOGIN_NUMBER_FIELD_ID)
            passwordField = self.driver.find_element_by_id(PASS_NUMBER_FIELD_ID)
            cardField.send_keys(card)
            passwordField.send_keys(password)
            result = True
        except NoSuchElementException:
            result = False

        return result

    def logoutUser(self):
        """
        Function which finds the logout submit button, and clicks it

        Returns:
            result (bool): Indicates if the logout submit button was clicked successfully
        """
        submitButton = self.driver.find_element_by_id(LOGOUT_SUBMIT_BUTTON_ID)
        submitButton.click()

        result = True
        return result

    def loadLoginFile(self, filename):
        """
        Function which loads the login tests file, and stores each test pair in class attribute variable

        Returns:
            result (bool): Indicates if login tests are successfully stored in variable
        """
        with open(filename, "r") as f:
            for line in f:
                self.loginInfo.append(line.split(","))

        result = True
        return result
        
if __name__ == "__main__":
    test_driver = Driver(CHROME_DRIVER_PATH)
