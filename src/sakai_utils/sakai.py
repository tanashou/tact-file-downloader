import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from typing import Any


class Sakai:
    def __init__(self) -> None:
        pass

    def __wait_for_page_load(self, driver: webdriver.Chrome) -> Any:
        return WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"  # type: ignore
        )

    def login(self) -> webdriver.Chrome:
        USERNAME = os.environ.get("TACT_USERNAME")
        PASSWORD = os.environ.get("TACT_PASSWORD")

        if USERNAME is None or PASSWORD is None:
            raise ValueError("環境変数にユーザー名とパスワードを設定してください")

        EMAIL_INPUT_BOX_ID = "i0116"
        CONFIRM_BUTTON_ID = "idSIButton9"
        PASSWORD_INPUT_BOX_ID = "i0118"
        ONETIME_PASSWORD_INPUT_BOX_ID = "idTxtBx_SAOTCC_OTC"
        VERIFY_BUTTON_ID = "idSubmit_SAOTCC_Continue"
        ACCEPT_BUTTON_XPATH = '//input[@name="_eventId_proceed"]'
        login_url = "https://tact.ac.thers.ac.jp/sakai-login-tool/container/"

        options = ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        driver.get(login_url)

        self.__wait_for_page_load(driver)
        email_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, EMAIL_INPUT_BOX_ID))
        )
        email_input.send_keys(USERNAME)

        self.__wait_for_page_load(driver)
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, CONFIRM_BUTTON_ID))
        )
        next_button.click()

        self.__wait_for_page_load(driver)
        password_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, PASSWORD_INPUT_BOX_ID))
        )
        password_input.send_keys(PASSWORD)
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, CONFIRM_BUTTON_ID))
        )
        sign_in_button.click()

        self.__wait_for_page_load(driver)
        otp_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, ONETIME_PASSWORD_INPUT_BOX_ID))
        )
        otp_input.send_keys(
            input("ワンタイムパスワードを入力してください:\n>")
        )  # TODO: OTPを生成して入力する手間を省きたい

        self.__wait_for_page_load(driver)
        verify_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, VERIFY_BUTTON_ID))
        )
        verify_button.click()

        self.__wait_for_page_load(driver)
        stay_signed_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, CONFIRM_BUTTON_ID))
        )
        stay_signed_in_button.click()

        self.__wait_for_page_load(driver)
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, ACCEPT_BUTTON_XPATH))
        )
        accept_button.click()

        self.__wait_for_page_load(driver)

        return driver

    def session_with_cookie(self, driver: webdriver.Chrome) -> requests.Session:
        cookies = driver.get_cookies()
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie["name"], cookie["value"])

        return session

    def perform_login_and_get_session(self) -> requests.Session:
        driver = None
        try:
            driver = self.login()
            session = self.session_with_cookie(driver)
            return session
        except TimeoutException as e:
            print("タイムアウトしました。もう一度試してください。")
            raise e
        finally:
            if driver is not None:
                driver.quit()


portal_url = "https://tact.ac.thers.ac.jp/portal"

if __name__ == "__main__":
    sakai = Sakai()
    session = sakai.perform_login_and_get_session()
    test_url = "https://tact.ac.thers.ac.jp/direct/site.json"
    response = session.get(test_url)
    print(response.text)
