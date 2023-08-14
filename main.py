import datetime
import time

import bs4
import pandas as pd
import pandas_market_calendars as market_cal
import requests
import schedule
from dateutil.parser import parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


def get_today_contango():
    table_id = driver.find_element(By.ID, 'basicTable')
    rows = table_id.find_elements(By.TAG_NAME, "td")
    contango_value = rows[0].text
    return contango_value


def move_to_history_page():
    driver.find_element(By.XPATH, "//a[@href='#fragment-2']").click()


def get_previous_day_data(curr_date, contango):
    for i in range(4):
        input_date = driver.find_element(By.ID, 'date1')
        input_date.clear()
        input_date.send_keys(curr_date)

        prev_button = driver.find_element(By.ID, 'bprevious')
        prev_button.click()
        get_button = driver.find_element(By.ID, 'b4')
        get_button.click()
        curr_date = input_date.get_attribute('value')
        parsed_date = parse(input_date.get_attribute('value')).date()

        time.sleep(5)
        source = driver.page_source
        soup = bs4.BeautifulSoup(source, 'html.parser')
        table_c3 = soup.find(id="c3")
        table = table_c3.find(id="basicTable")
        con = table.find_all('td')
        contango[parsed_date] = con[0].text

    return contango


def get_past_five_days_data():
    global driver
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1200")
    DRIVER_PATH = Service('C:\\Users\\ranar\\Programs\\chromedriver_win32\\chromedriver.exe')
    driver = webdriver.Chrome(options=options, service=DRIVER_PATH)
    driver.get('http://vixcentral.com/')
    # Find contango of today
    today_contango = get_today_contango()
    # Go to history
    move_to_history_page()
    date = datetime.date.today().strftime('%B %d, %Y')
    contangoData = {datetime.date.today(): today_contango}
    get_previous_day_data(date, contangoData)
    driver.quit()
    # Output to be sent
    headers = ["Date", "Contango"]
    # print(pd.DataFrame(contangoData.items(), columns=headers).to_string(index=False))
    return pd.DataFrame(contangoData.items(), columns=headers).to_string(index=False)


def is_market_open(date):
    result = market_cal.get_calendar('NYSE').schedule(start_date=date, end_date=date)
    return result.empty is False


def telegram_bot_send_text(bot_message):
    bot_token = '6657968793:AAGnAT36Poce83gGTu7Dg9XSyttewo6DBnA'
    bot_chatID = '-733472703'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&text=' + bot_message

    if is_market_open(datetime.date.today()):
        response = requests.get(send_text)
        print("Msg sent on ", datetime.datetime.now(), " ", response)


def send_message():
    data = get_past_five_days_data()
    telegram_bot_send_text(data)


schedule.every().monday.at("21:00").do(send_message)
schedule.every().tuesday.at("21:00").do(send_message)
schedule.every().wednesday.at("21:00").do(send_message)
schedule.every().thursday.at("21:00").do(send_message)
schedule.every().friday.at("21:00").do(send_message)
schedule.every(10).seconds.do(send_message)

while True:
    schedule.run_pending()
    time.sleep(1)
