import json
import time
import traceback
from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions


class Bank(Enum):
    hsbchk = "hsbchk"


class BankNavigator(object):
    def __init__(self, driver, config):
        self.driver = driver
        self.config = config

    def login_url(self):
        if self.bank() is Bank.hsbchk.value:
            return "https://www.ebanking.hsbc.com.hk"
        else:
            raise Exception('Bank not supported')

    def bank(self):
        raise NotImplementedError()

    def navigate(self):
        raise NotImplementedError()

    def login(self):
        raise NotImplementedError()

    def check_balance(self):
        raise NotImplementedError()


class Hsbc(BankNavigator):
    def bank(self):
        return Bank.hsbchk.value

    def navigate(self):
        self.driver.get(self.login_url())
        assert 'Personal Internet Banking' in self.driver.title

    def login(self):
        user_elem = self.driver.find_element_by_name('u_UserID')
        user_elem.send_keys(self.config['user'])

        # returns only first match
        self.driver \
            .find_element_by_css_selector('.logonmode > a') \
            .click()
        assert 'Log on to Internet Banking:' in self.driver.title

        memorable_elem = self.driver.find_element_by_id('memorableAnswer')
        memorable_elem.send_keys(self.config['pass1'])

        smallest_elems = self.driver.find_elements_by_class_name('smallestInput')
        for i in range(len(smallest_elems)):
            smallest_elem = smallest_elems[i]
            if 'active' in smallest_elem.get_attribute('class'):
                smallest_elem.send_keys(self.config['pass2'][i])

        self.driver.find_element_by_class_name('submit_input').click()
        try:
            WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.ID, 'Manage')))
        finally:
            assert 'My banking' in self.driver.title

    def check_balance(self):
        bundles = self.driver.find_elements_by_class_name('bundledAccountTitle')
        for i in range(len(bundles)):
            time.sleep(0.5)
            bundles[i].click()

        for account in self.config['accounts']:
            if 'sub' in account:
                # TODO: implement bundledAccountContent loop to read each subaccount
                pass
            else:
                parent_elem = self.driver \
                    .find_element_by_xpath('//span[contains(@class, "itemName") and contains(text(), "{}")]/..'
                                           .format(account['account']))
                value_elem = parent_elem.find_element_by_class_name('itemValue')
                print(value_elem.text)


def get_config():
    with open('config.json') as f:
        config = json.loads(f.read())
    return config


def get_driver():
    driver = webdriver.Firefox()
    return driver


def iterate_portals(driver, config):
    for x in config['portals']:
        navigator = None

        if x['bank'] == Bank.hsbchk.value:
            navigator = Hsbc(driver, x)
        else:
            raise Exception('Bank not supported')

        try:
            navigator.navigate()
            navigator.login()
            navigator.check_balance()
        except Exception as e:
            print("Error: %s" % e)
            print(traceback.format_exc())
            driver.quit()


def main():
    driver = get_driver()
    config = get_config()

    iterate_portals(driver, config)

    print("Quitting...")
    # driver.quit()


if __name__ == "__main__":
    main()
