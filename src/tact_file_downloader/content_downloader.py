from requests.cookies import RequestsCookieJar
import requests
from sakai_content import SakaiContent
import os


class ContentDownloader:
    def __init__(
        self, cookie_jar: RequestsCookieJar, save_root_path: str | None = None
    ) -> None:
        self.cookie_jar = cookie_jar
        self.save_root_path = save_root_path or os.getcwd()

    def download_and_save_file(self, content: SakaiContent) -> None:
        session = requests.Session()
        session.cookies.update(self.cookie_jar)
        response = session.get(content.url, stream=True)

        # Ensure the directory exists
        directory_path = os.path.join(self.save_root_path, content.path)
        os.makedirs(directory_path, exist_ok=True)

        save_path = os.path.join(directory_path, content.title)

        if os.path.isfile(save_path):
            return

        if response.status_code == 200:
            with open(save_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        file.write(chunk)
            print(f"File downloaded successfully to {save_path}")
        else:
            print(f"Failed to download the file. Status code: {response.status_code}")
