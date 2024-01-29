from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import os, schedule, subprocess, sys, time

username = os.environ.get('FL_USERNAME', None)
password = os.environ.get('FL_PASSWORD', None)
interval = os.environ.get('CHECK_INTERVAL', None)

use_driver = "local"

if username is None:
    print("Error: FL_USERNAME is not set.")
    sys.exit(1)

if password is None:
    print("Error: FL_PASSWORD is not set.")
    sys.exit(1)

if int(interval) < 5 or interval is None:
    print("Error: Set an interval more than 10 minutes. Don't hammer the website.")
    sys.exit(1)


def get_public_ip():
    try:
        myip = subprocess.run(['dig', '-4', 'TXT', '+short', 'o-o.myaddr.l.google.com', '@ns1.google.com'],
                              capture_output=True, text=True)
    except Exception as e:
        print("Error: {}".format(e))
        os.exit(1)
    else:
        return myip.stdout.replace('"', '')


def driver_init():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    driver.implicitly_wait(10)

    return driver


def get_fl_ip(driver):
    driver.get('https://filelist.io/login.php?returnto=%2Fmy.php')
    # print(driver.title)

    username_field = driver.find_element(By.XPATH, '//*[@id="username"]')  # Find the search box
    username_field.send_keys(username)

    password_field = driver.find_element(By.XPATH, '//*[@id="password"]')
    password_field.send_keys(password + Keys.RETURN)

    # driver.save_screenshot("screenshot.png")

    redirected_url = driver.current_url
    if redirected_url == "https://filelist.io/takelogin.php":
        print("Check your filelist username and password. Check your compose file and recreate container")
        sys.exit(1)

    # results = driver.find_element(By.XPATH, '//*[@id="maincolumn"]/div/div[5]/div/div[2]/form/fieldset[17]/label/input')
    whitelist_field = driver.find_element(By.NAME, 'whitelistip')
    fl_ip = whitelist_field.get_attribute('value')

    return fl_ip


def set_fl_ip(ip, driver):
    driver.get('https://filelist.io/login.php?returnto=%2Fmy.php')
    # print(driver.title)

    username_field = driver.find_element(By.XPATH, '//*[@id="username"]')  # Find the search box
    username_field.send_keys(username)

    password_field = driver.find_element(By.XPATH, '//*[@id="password"]')
    password_field.send_keys(password + Keys.RETURN)

    whitelist_field = driver.find_element(By.NAME, 'whitelistip')
    whitelist_field.clear()
    whitelist_field.send_keys(ip)

    form = driver.find_element(By.NAME, "myForm")
    form.submit()

    return


def check_ip(driver):
    public_ip = get_public_ip()
    fl_ip = get_fl_ip(driver)

    current_datetime = datetime.now()

    if public_ip != fl_ip:
        print(
            "{} - Your public IP is {} and the one in FL profile is {}. Proceeding to change.".format(current_datetime,
                                                                                                      public_ip, fl_ip))
        set_fl_ip(public_ip, driver)
    else:
        print("{} - Your IP address is updated".format(current_datetime))


driver = driver_init()

# Trigger an initial check - Be careful. You might get baned for an hour if you have your credentials wrong.
check_ip(driver)

print("Using {} driver. Waiting {} minute for the first check".format(use_driver, interval))

# Schedule the task to run every x minutes
schedule.every(int(interval)).minutes.do(check_ip, driver)

while True:
    schedule.run_pending()
    time.sleep(2)
