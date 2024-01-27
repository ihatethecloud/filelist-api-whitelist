from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from urllib.request import urlopen
from datetime import datetime
import os, sys, schedule, time


username = os.environ.get('FL_USERNAME', None)
password = os.environ.get('FL_PASSWORD', None)
chrome_driver = os.environ.get('DRIVER', None)
interval = os.environ.get('CHECK_INTERVAL', None)

use_driver = "http://" + chrome_driver + ":3000/webdriver"

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
        myip = urlopen("http://ifconfig.me/ip")
    except HTTPError as e:
        print('Error code: ', e.code)
        os.exit(1)
    except URLError as e:
        print('Reason: ', e.reason)
        os.exit(1)
    else:
        return myip.read().decode('utf-8')

def driver_init():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")

    driver = webdriver.Remote(
        command_executor=use_driver,
        options=chrome_options
    )

    driver.implicitly_wait(10)

    return driver

def get_fl_ip(driver):
    driver.get('https://filelist.io/login.php?returnto=%2Fmy.php')
    # print(driver.title)

    username_field = driver.find_element(By.XPATH, '//*[@id="username"]')  # Find the search box
    username_field.send_keys(username)


    password_field = driver.find_element(By.XPATH, '//*[@id="password"]')
    password_field.send_keys(password + Keys.RETURN)

    #driver.save_screenshot("screenshot.png")

    redirected_url = driver.current_url
    if redirected_url == "https://filelist.io/takelogin.php":
        print("Check your filelist username and password. Check your compose file and recreate container")
        sys.exit(1)

    #results = driver.find_element(By.XPATH, '//*[@id="maincolumn"]/div/div[5]/div/div[2]/form/fieldset[17]/label/input')
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

    #results = driver.find_element(By.XPATH, '//*[@id="maincolumn"]/div/div[5]/div/div[2]/form/fieldset[17]/label/input')
    whitelist_field = driver.find_element(By.NAME, 'whitelistip')
    whitelist_field.clear()
    whitelist_field.send_keys(ip)
    
    form = driver.find_element(By.NAME, "myForm")
    form.submit()
    
    driver.save_screenshot("screenshot.png")
    return

def check_ip(driver):
    public_ip = get_public_ip()
    fl_ip = get_fl_ip(driver)

    current_datetime = datetime.now()

    if public_ip != fl_ip:
        print("{} - Your public IP is {} and the one in FL profile is {}. Proceeding to change.".format(current_datetime, public_ip, fl_ip))
        set_fl_ip(public_ip, driver)
    else:
        print("{} - Your IP address is updated".format(current_datetime))


driver = driver_init()

# Trigger an initial check - Be careful. You might get baned for an hour if you have your credentials wrong.
# check_ip()

print("Using {} driver. Waiting {} minute for the first check".format(use_driver, interval))

# Schedule the task to run every x minutes
schedule.every(10).minutes.do(check_ip(driver))

while True:
    schedule.run_pending()
    time.sleep(2)