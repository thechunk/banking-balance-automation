import time
import re
from enum import Enum
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions


class BankIdentifier(Enum):
    hsbchk = "hsbchk"


class BankCrawler(object):
    def __init__(self, driver, config):
        self.driver = driver
        self.config = config

    def login_url(self):
        if self.bank() is BankIdentifier.hsbchk.value:
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


class _BankStringMethods(object):
    @staticmethod
    def format_balance_values(s):
        return ''.join(re.findall('[\d.\-]+', s))


class Hsbc(BankCrawler):
    def bank(self):
        return BankIdentifier.hsbchk.value

    def navigate(self):
        self.driver.get(self.login_url())
        assert 'Personal Internet Banking' in self.driver.title

    def login(self):
        user_elem = self.driver.find_element_by_name('u_UserID')
        user_elem.send_keys(self.config['user'])

        # returns only first button
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
            WebDriverWait(self.driver, 20).until(expected_conditions.presence_of_element_located((By.ID, 'Manage')))
        finally:
            assert 'My banking' in self.driver.title

    def check_balance(self):
        bundles = self.driver.find_elements_by_class_name('bundledAccountTitle')
        for i in range(len(bundles)):
            time.sleep(1.0)
            bundles[i].click()

        balances = {}
        for account in self.config['accounts']:
            account_num = account['account']
            balances[account_num] = None

            if 'sub' in account:
                balances[account_num] = {}
                parent_elem = self.driver.find_element_by_css_selector('[accountnumber="{}"]'.format(account_num))

                for sub in account['sub']:
                    child_elem = parent_elem.find_element_by_xpath(
                        '//span[contains(@class, "itemTitle") and contains(text(), "{}")]/../..'.format(sub)
                    )
                    value_elem = child_elem.find_element_by_class_name('itemValue')
                    balances[account_num][sub] = _BankStringMethods.format_balance_values(value_elem.text)
            else:
                parent_elem = self.driver \
                    .find_element_by_xpath('//span[contains(@class, "itemName") and contains(text(), "{}")]/..'
                                           .format(account_num))
                account_name_elem = parent_elem.find_element_by_css_selector('.itemTitle > .itemTitle')
                value_elem = parent_elem.find_element_by_class_name('itemValue')

                account_name = account_name_elem.text.splitlines(keepends=False)[-1]
                balances[account_num] = {account_name: _BankStringMethods.format_balance_values(value_elem.text)}

        return balances
