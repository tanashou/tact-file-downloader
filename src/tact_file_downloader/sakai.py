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
import pyotp
from urllib.parse import urlparse, parse_qs

# cannot import like 'from tact_file_downloader.sakai_site import SakaiSite'
from sakai_site import SakaiSite
from paginated_list import PaginatedList
from requester import Requester
from sakai_content import SakaiContent


class Sakai:
    def __init__(self, base_url: str) -> None:
        self.BASE_URL = base_url
        cookie_jar = self._get_cookiejar()
        self.requester = Requester(self.BASE_URL, cookie_jar)

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

    def wait_for_page_load(self, driver: webdriver.Chrome) -> Any:
        return WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"  # type: ignore
        )

    def _login(self) -> webdriver.Chrome:
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
        login_url = f"{self.BASE_URL}sakai-login-tool/container/"

        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--log_level=3")
        driver = webdriver.Chrome(options=options)
        driver.get(login_url)

        self.wait_for_page_load(driver)
        email_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, EMAIL_INPUT_BOX_ID))
        )
        email_input.send_keys(USERNAME)

        self.wait_for_page_load(driver)
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, CONFIRM_BUTTON_ID))
        )
        next_button.click()

        self.wait_for_page_load(driver)
        password_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, PASSWORD_INPUT_BOX_ID))
        )
        password_input.send_keys(PASSWORD)
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, CONFIRM_BUTTON_ID))
        )
        sign_in_button.click()

        self._transition_to_otp_input_window(driver)

        self.wait_for_page_load(driver)
        otp_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, ONETIME_PASSWORD_INPUT_BOX_ID))
        )

        otp = self._get_otp()
        otp_input.send_keys(otp)

        self.wait_for_page_load(driver)
        verify_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, VERIFY_BUTTON_ID))
        )
        verify_button.click()

        self.wait_for_page_load(driver)
        stay_signed_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, CONFIRM_BUTTON_ID))
        )
        stay_signed_in_button.click()

        self.wait_for_page_load(driver)
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, ACCEPT_BUTTON_XPATH))
        )
        accept_button.click()

        self.wait_for_page_load(driver)

        return driver

    def get_site_collection(self) -> list[SakaiSite]:
        def parse_to_sites(json_list: list[dict[Any, Any]]) -> list[SakaiSite]:
            result = []
            for json_data in json_list:
                for site in json_data["site_collection"]:
                    result.append(SakaiSite(title=site["title"], id=site["id"]))
            return result

        endpoint = "direct/site.json"
        url = f"{self.BASE_URL}{endpoint}"
        sites_json = PaginatedList(
            self.requester, url, key="site_collection"
        ).get_all_json()

        return parse_to_sites(sites_json)

    def get_contents(self, site_id: str, site_title: str) -> list[SakaiContent]:
        def parse_to_contents(json_data: dict[Any, Any]) -> list[SakaiContent]:
            result = []
            for content in json_data["content_collection"]:
                result.append(
                    SakaiContent(
                        container=content["container"],
                        title=content["title"],
                        type=content["type"],
                        url=content["url"],
                        site_title=site_title,
                    )
                )
            return result

        endpoint = f"direct/content/site/{site_id}.json"
        response = self.requester.request("GET", _url=f"{self.BASE_URL}{endpoint}")
        return parse_to_contents(response.json())

    def _get_otp(self) -> str:
        otp_uri = os.getenv("TACT_OTP_URI")

        if otp_uri:
            parsed_uri = urlparse(otp_uri)
            query_params = parse_qs(parsed_uri.query)

            if "secret" in query_params:
                secret_key = query_params["secret"][0]
                totp = pyotp.TOTP(secret_key)
                otp = totp.now()

                return otp
            else:
                raise ValueError(
                    "ワンタイムパスワードを生成できませんでした。URIが正しいか確認してください。"
                )
        else:
            return input("ワンタイムパスワードを入力してください:\n>")

    def _transition_to_otp_input_window(self, driver) -> None:
        self.wait_for_page_load(driver)
        change_sign_in_mode_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "signInAnotherWay"))
        )
        change_sign_in_mode_button.click()

        self.wait_for_page_load(driver)
        use_verification_code_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'div[data-value="PhoneAppOTP"]')
            )
        )
        use_verification_code_button.click()

    def _get_favorite_sites_id(self) -> list[str]:
        endpoint = "portal/favorites/list.json"
        response = self.requester.request("GET", _url=f"{self.BASE_URL}{endpoint}")
        return response.json()["favoriteSiteIds"]

    def get_favorite_sites(self) -> list[SakaiSite]:
        result = []

        sites_id = self._get_favorite_sites_id()
        for site_id in sites_id:
            endpoint = f"direct/site/{site_id}.json"
            response = self.requester.request("GET", _url=f"{self.BASE_URL}{endpoint}")
            json_data = response.json()
            result.append(SakaiSite(title=json_data["title"], id=site_id))

        return result
