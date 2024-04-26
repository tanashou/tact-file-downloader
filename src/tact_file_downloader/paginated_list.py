from requester import Requester
from typing import Any


class PaginatedList:
    # Repeat the request until the target data is an empty list. The key is the JSON key name of the target data.
    def __init__(self, requester: Requester, full_url: str, key: str) -> None:
        self.requester = requester
        self.url = full_url
        self.key = key

    def get_all_json(self) -> list[Any]:
        result = []
        start = 1
        limit = 50

        while True:
            params = {
                "_start": start,
                "_limit": limit,
            }

            response = self.requester.request("GET", _url=self.url, _params=params)
            json_data = response.json()
            if json_data[self.key] == []:
                break

            result.append(json_data)
            start += limit

        return result
