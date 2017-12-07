import json
import traceback
from bank.crawler import BankIdentifier, Hsbc
from connectors.googlesheets import GoogleSheetsConnector
from data.bridge import AccountSummarySheetBridge
from selenium import webdriver

def get_config():
    with open('config.json') as f:
        config = json.loads(f.read())
    return config


def get_driver():
    driver = webdriver.Firefox()
    return driver


def iterate_portals(driver, config):
    balances = {}

    for x in config['portals']:
        navigator = None
        key = x['bank']

        if key == BankIdentifier.hsbchk.value:
            navigator = Hsbc(driver, x)
        else:
            raise Exception('Bank not supported')

        balances[key] = None
        try:
            navigator.navigate()
            navigator.login()
            balances[key] = navigator.check_balance()
        except Exception as e:
            print("Error: %s" % e)
            print(traceback.format_exc())
            driver.quit()

    return balances

def main():
    driver = get_driver()
    config = get_config()

    balance = iterate_portals(driver, config)

    gs = GoogleSheetsConnector()
    as_bridge = AccountSummarySheetBridge(gs)
    as_bridge.add_values(balance['hsbchk']) #TODO: allow add_values for generalized bank keys
    as_bridge.commit_rows()

    print("Quitting...")
    driver.quit()


if __name__ == "__main__":
    main()
