import os
import smtplib
import ssl
import sys
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv


def send_mail():
    port = 465  # For SSL
    password = os.getenv("EMAIL_SENDER_PW")  # does not work with 2FA available accounts. also email should be activated to work on less secure apps

    # Create a secure SSL context
    context = ssl.create_default_context()
    sender_email = os.getenv("SENDER_EMAIL")
    receiver = os.getenv("RECEIVER_EMAIL")

    message = """\
    Subject: IBB Halı Saha Bulucu.

    Açıkta slot var, kontrol etmeyi unutma."""

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver, message)


def available():
    if driver.current_url is "https://online.spor.istanbul/uyegiris":
        login()

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
    day = content.find_elements_by_tag_name("div")[map_day(os.getenv("REQUESTED_DAY"))]

    try:
        midnight = day.find_element_by_xpath("//span[.='{}']".format(os.getenv("REQUESTED_TIME_RANGE")))
    except Exception:
        print("Time range does does not available at this moment.")
        return False

    status = midnight.find_element_by_xpath("./preceding-sibling::div")

    try:
        status.find_element_by_class_name("labelUfak")
        print("Still not available.")
        return False
    except NoSuchElementException:
        print("Opening found, sending mail...")
        return True


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
    chrome_options.add_argument("window-size=1900,1080");
    chrome = webdriver.Chrome(options=chrome_options)
    return chrome


def open_login_page():
    driver.get("https://online.spor.istanbul/uyegiris")


def start_job():
    if available():
        send_mail()
        sys.exit()
    else:
        print("still closed refreshing after ", retry_in_sec, " seconds")
        time.sleep(int(retry_in_sec))
        driver.refresh()
        start_job()


if __name__ == '__main__':
    load_dotenv()
    retry_in_sec = os.getenv("RETRY_IN_SEC")
    driver = get_driver()
    login()
    start_job()
