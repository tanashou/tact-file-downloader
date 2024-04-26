import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from typing import Any
from requests.utils import cookiejar_from_dict
from requests.cookies import RequestsCookieJar

# TODO: 先頭に tact_file_downloader をつけたい
from sakai_site import SakaiSite
from paginated_list import PaginatedList
from requester import Requester


class Sakai:
    BASE_URL = "https://tact.ac.thers.ac.jp/"

    def __init__(self) -> None:
        cookie_jar = self._get_cookiejar()
        self.__requester = Requester(self.BASE_URL, cookie_jar)

    def _get_cookiejar(self) -> RequestsCookieJar:
        driver = None
        selenium_cookies = None
        try:
            driver = self._login()
            selenium_cookies = driver.get_cookies()
        except TimeoutException as e:
            print("タイムアウトしました。もう一度試してください。")
            raise e
        finally:
            if driver is not None:
                driver.quit()
        cookie_dict = {cookie["name"]: cookie["value"] for cookie in selenium_cookies}
        return cookiejar_from_dict(cookie_dict)  # type: ignore

    def _login(self) -> webdriver.Chrome:
        def wait_for_page_load(driver: webdriver.Chrome) -> Any:
            return WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"  # type: ignore
            )

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

        wait_for_page_load(driver)
        email_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, EMAIL_INPUT_BOX_ID))
        )
        email_input.send_keys(USERNAME)

        wait_for_page_load(driver)
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, CONFIRM_BUTTON_ID))
        )
        next_button.click()

        wait_for_page_load(driver)
        password_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, PASSWORD_INPUT_BOX_ID))
        )
        password_input.send_keys(PASSWORD)
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, CONFIRM_BUTTON_ID))
        )
        sign_in_button.click()

        wait_for_page_load(driver)
        otp_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, ONETIME_PASSWORD_INPUT_BOX_ID))
        )
        otp_input.send_keys(
            input("ワンタイムパスワードを入力してください:\n>")
        )  # TODO: OTPを生成して入力する手間を省きたい

        wait_for_page_load(driver)
        verify_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, VERIFY_BUTTON_ID))
        )
        verify_button.click()

        wait_for_page_load(driver)
        stay_signed_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, CONFIRM_BUTTON_ID))
        )
        stay_signed_in_button.click()

        wait_for_page_load(driver)
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, ACCEPT_BUTTON_XPATH))
        )
        accept_button.click()

        wait_for_page_load(driver)

        return driver

    def get_site_collection(self) -> list[SakaiSite]:
        def parse_to_sites(json_list: list[dict[Any, Any]]) -> list[SakaiSite]:
            result = []
            for json_data in json_list:
                for site in json_data["site_collection"]:
                    result.append(SakaiSite(title=site["title"], id=site["id"]))

            return result

        endpoint = "direct/site.json"
        url = self.BASE_URL + endpoint
        sites_json = PaginatedList(
            self.__requester, url, key="site_collection"
        ).get_all_json()

        return parse_to_sites(sites_json)

    # def get_site_content_collection


if __name__ == "__main__":
    sakai = Sakai()
    sites = sakai.get_site_collection()
    for site in sites:
        print(site)

    # for site in sites.sites:
    #     print(site)
