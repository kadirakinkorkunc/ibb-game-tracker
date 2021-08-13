import os
import smtplib
import ssl
import sys
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
from email.message import EmailMessage


def send_mail(action):
    print("sending mail...")
    port = 465  # For SSL
    password = os.getenv("EMAIL_SENDER_PW")  # does not work with 2FA available accounts. also email should be activated to work on less secure apps

    # Create a secure SSL context
    context = ssl.create_default_context()
    sender_email = os.getenv("SENDER_EMAIL")
    receivers = os.getenv("RECEIVER_EMAILS")
    requested_day = os.getenv("REQUESTED_DAY")
    requested_time = os.getenv("REQUESTED_TIME_RANGE")

    msg = EmailMessage()
    msg['Subject'] = 'Hey, we have news about the pitch!'
    msg['From'] = sender_email
    msg['To'] = receivers

    if action == "ADD_TO_BASKET":
        message = "Checkout your basket in 12 hours, we made a cart reservation for {} - {}. " \
                  "Go https://online.spor.istanbul now!".format(requested_day, requested_time)
    elif action == "WARN":
        message = "There is an open slot for your choice({} - {}). " \
                  "Go https://online.spor.istanbul now!".format(requested_day, requested_time)

    msg.set_content(message)

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receivers, msg.as_string())
        print("mail sent, exiting...")
        server.quit()


def find_next_x_day(day_index, day_elements, requested_time_range):
    try:
        requested_day = day_elements[day_index]
        time_range = requested_day.find_element_by_xpath("//span[.='{}']".format(requested_time_range))
        print("There is a time range exist in this week.")
    except NoSuchElementException:
        try:
            print("Couldn't find at the first element, trying to find in next week if it exists.")
            time_range = day_elements[day_index + 8].find_element_by_xpath(
                "//span[.='{}']".format(requested_time_range))
            print("There is a time range exists in next week.")
        except NoSuchElementException:
            print("Couldn't find in next week either...")
            return None
    return time_range


def get_required_element_if_available():
    if driver.current_url == "https://online.spor.istanbul/uyegiris":
        login()

    if driver.current_url != "https://online.spor.istanbul/satiskiralik":
        driver.get("https://online.spor.istanbul/satiskiralik")

    Select(driver.find_element_by_name("ctl00$pageContent$ddlBransFiltre")).select_by_value(
        os.getenv("GAME_ID"))  # game

    facility_id = os.getenv("FACILITY_ID");
    WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located(
        (By.CSS_SELECTOR, "option[value='{}']".format(facility_id))))
    Select(driver.find_element_by_name("ctl00$pageContent$ddlTesisFiltre")).select_by_value(
        "{}".format(facility_id))  # facility

    pitch_id = os.getenv("PITCH_ID")
    WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located(
        (By.CSS_SELECTOR, "option[value='{}']".format(pitch_id))))
    Select(driver.find_element_by_name("ctl00$pageContent$ddlSalonFiltre")).select_by_value(
        "{}".format(pitch_id))  # pitch

    WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.ID, 'pageContent_Div1')))
    content = driver.find_element_by_id("pageContent_Div1")
    days = content.find_elements_by_tag_name("div")

    requested_day = os.getenv("REQUESTED_DAY")
    requested_time = os.getenv("REQUESTED_TIME_RANGE")
    time_range = find_next_x_day(map_day(requested_day), days, requested_time)
    print("Day: ", requested_day, "- Time: ", requested_time)
    if time_range is not None:
        try:
            clickable = time_range.find_element_by_xpath("./following-sibling::a")
            return clickable
        except NoSuchElementException:
            return None
    return None


def map_day(day):
    days = ["pazartesi", "sali", "çarşamba", "perşembe", "cuma", "cumartesi", "pazar"]
    day = day.lower()
    return days.index(day)


def login():
    open_login_page()
    driver.find_element_by_name("txtTCPasaport").send_keys(os.getenv("MEMBER_TCKNO"))
    driver.find_element_by_name("txtSifre").send_keys(os.getenv("MEMBER_PW"))
    driver.find_element_by_name("btnGirisYap").send_keys(Keys.ENTER)

    try:
        driver.find_element_by_link_text("Kiralama Hizmetleri").click()
    except NoSuchElementException:
        print("Couldn't log in the site, exiting...")
        sys.exit()


def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("no-sandbox")
    chrome_options.add_argument("headless")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("window-size=1900,1080")
    chrome = webdriver.Chrome(options=chrome_options)
    return chrome


def open_login_page():
    driver.get("https://online.spor.istanbul/uyegiris")


def add_to_basket(clickable):
    print("Opening found, trying to add to basket")
    driver.execute_script("arguments[0].click()", clickable)
    WebDriverWait(driver, 10).until(expected_conditions.alert_is_present())
    driver.switch_to.alert.accept()
    WebDriverWait(driver, 10).until(
        expected_conditions.presence_of_element_located((By.ID, 'pageContent_cboxKiralikSatisSozlesmesi')))
    driver.find_element_by_id("pageContent_cboxKiralikSatisSozlesmesi").click()
    WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.ID, 'pageContent_lbtnSepeteEkle')))
    driver.find_element_by_id("pageContent_lbtnSepeteEkle").click()
    WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located((By.ID, 'pageContent_btnOdemeYap')))


def retry():
    print("still closed, will retry after ", retry_in_sec, " seconds")
    print("------------")
    time.sleep(int(retry_in_sec))
    driver.refresh()
    start_job()


def start_job():
    action = os.getenv("ACTION")

    try:
        clickable = get_required_element_if_available()

        if clickable is not None:
            if action == "ADD_TO_BASKET":
                add_to_basket(clickable)
            send_mail(action)
            sys.exit(0)
        else:
            retry()
    except TimeoutException:
        print("timeout exception occurred, trying again...")
        start_job()


if __name__ == '__main__':
    load_dotenv()
    retry_in_sec = os.getenv("RETRY_IN_SEC")
    driver = get_driver()
    login()
    start_job()
