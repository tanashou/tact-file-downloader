from requests.cookies import RequestsCookieJar
import requests
from typing import Any


class Requester:
    def __init__(self, base_url: str, cookie_jar: RequestsCookieJar):
        self.base_url = base_url
        self.cookie_jar = cookie_jar
        self._session = requests.Session()

    def _get_request(
        self, url: str, headers: dict[str, str], params: dict[str, Any] | None = None
    ) -> requests.Response:
        return self._session.get(url, headers=headers, params=params)

    def request(
        self,
        method: str,
        endpoint: str | None = None,
        headers: dict[str, str] | None = None,
        _url: str | None = None,
        _params: dict[str, Any] | None = None,
    ) -> requests.Response:
        full_url = _url if _url else f"{self.base_url}{endpoint}"

        if not headers:
            headers = {}

        _params = _params or {}

        match method:
            case "GET":
                req_method = self._get_request
            case "POST":
                pass
            case "DELETE":
                pass
            case "PUT":
                pass
            case "PATCH":
                pass

        try:
            response = req_method(full_url, headers, _params)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")

        return response
