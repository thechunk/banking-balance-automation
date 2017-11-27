import configparser
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

class BankNavigator(object):
    def __init__(self, driver, config):
        self.driver = driver
        self.config = config

    def navigate(self):
        raise NotImplementedError()

    def login(self):
        raise NotImplementedError()

    def check_balance(self):
        raise NotImplementedError()

class Hsbc(BankNavigator):
    def navigate(self):
        self.driver.get(self.config['hsbc.com.hk']['LoginUrl'])
        assert 'Personal Internet Banking' in self.driver.title

    def login(self):
        userElem = self.driver.find_element_by_name('u_UserID')
        userElem.send_keys(self.config['hsbc.com.hk']['User'])

        # returns only first match
        self.driver \
            .find_element_by_css_selector('.logonmode > a') \
            .click()
        assert 'Log on to Internet Banking:' in self.driver.title

        memorableElem = self.driver.find_element_by_id('memorableAnswer')
        memorableElem.send_keys(self.config['hsbc.com.hk']['Pass1'])

        smallestElems = self.driver.find_elements_by_class_name('smallestInput')
        for i in range(len(smallestElems)):
            smallestElem = smallestElems[i]
            if ('active' in smallestElem.get_attribute('class')):
                smallestElem.send_keys(self.config['hsbc.com.hk']['Pass2'][i])

        self.driver.find_element_by_class_name('submit_input').click()
        try:
            WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.ID, 'Manage')))
        finally:
            assert 'My banking' in self.driver.title

    def check_balance(self):
        bundles = self.driver.find_elements_by_class_name('bundledAccountTitle')
        for i in range(len(bundles)):
            time.sleep(1)
            bundles[i].click()

def get_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

def get_driver():
    driver = webdriver.Firefox()
    return driver

def main():
    driver = get_driver()
    config = get_config()

    hsbc = Hsbc(driver, config)
    try:
        hsbc.navigate()
        hsbc.login()
        hsbc.check_balance()
    except Exception as e:
        print("Error: %s" % e)
        driver.quit()

    print("Quitting...")
    # driver.quit()

if __name__ == "__main__":
    main()
