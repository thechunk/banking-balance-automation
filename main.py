import json
import traceback
from bank.navigator import BankIdentifier, Hsbc
from selenium import webdriver

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

        if x['bank'] == BankIdentifier.hsbchk.value:
            navigator = Hsbc(driver, x)
        else:
            raise Exception('Bank not supported')

        try:
            navigator.navigate()
            navigator.login()
            print(navigator.check_balance())
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
