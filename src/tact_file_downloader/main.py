from sakai import Sakai
from content_downloader import ContentDownloader
from multiprocessing import Pool
from directory_selector import DirectorySelector
from typing import Any
import os


def download_process(args: Any) -> None:
    content, cookie_jar, save_root_path = args
    downloader = ContentDownloader(cookie_jar, save_root_path)
    downloader.download_and_save_file(content)


def main() -> None:
    POOL_SIZE = 8
    BASE_URL = "https://tact.ac.thers.ac.jp/"

    sakai = Sakai(BASE_URL)
    sites = sakai.get_favorite_sites()
    selector = DirectorySelector()
    tasks = []
    for site in sites:
        contents = sakai.get_contents(site.id, site.title)
        for content in contents:
            # if the type is 'collection', it is a folder. otherwise, it is a file.
            if content.is_site_root:
                # create directory for the site. it creates a directory if there was no contents in the site.
                # check if the directory exists to avoid creating a directory for the site with no contents.
                if not os.path.exists(
                    os.path.join(selector.save_root_path, content.title)
                ):
                    os.makedirs(
                        os.path.join(selector.save_root_path, content.title),
                        exist_ok=True,
                    )
                    print(f"Created directory: {content.title}")
            elif content.type != "collection":
                task = (content, sakai.requester.cookie_jar, selector.save_root_path)
                tasks.append(task)

    with Pool(POOL_SIZE) as pool:
        pool.map(download_process, tasks)


if __name__ == "__main__":
    main()
