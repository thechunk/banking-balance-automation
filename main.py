import json
import traceback
from bank.crawler import BankIdentifier, Hsbc
from connectors.googlesheets import GoogleSheetsConnector
from data.processing import RawDataProcessor
from selenium import webdriver

def get_config():
    with open('config.json') as f:
        config = json.loads(f.read())
    return config


def get_driver():
    driver = webdriver.Firefox()
    return driver


def iterate_portals(driver, config):
    balances = {} # TODO: return balances in generalized format

    for x in config['portals']:
        navigator = None

        if x['bank'] == BankIdentifier.hsbchk.value:
            navigator = Hsbc(driver, x)
        else:
            raise Exception('Bank not supported')

        balance = None
        try:
            navigator.navigate()
            navigator.login()
            balance = navigator.check_balance()
        except Exception as e:
            print("Error: %s" % e)
            print(traceback.format_exc())
            driver.quit()

        return balance

def main():
    driver = get_driver()
    config = get_config()

    balance = iterate_portals(driver, config)

    gs = GoogleSheetsConnector()
    values = RawDataProcessor.banks_to_rows(balance)
    if gs.initialized():
        gs.append_row(values)
    else:
        gs.append_rows(RawDataProcessor.banks_to_headers(balance).append(values))

    print("Quitting...")
    driver.quit()


if __name__ == "__main__":
    main()
