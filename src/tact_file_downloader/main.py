from sakai import Sakai
from content_downloader import ContentDownloader
import os
from multiprocessing import Pool

save_root_path = ""
POOL_SIZE = 8


def download_process(args):
    content, cookie_jar, save_root_path = args
    downloader = ContentDownloader(cookie_jar, save_root_path)
    downloader.download_and_save_file(content)


def main():
    global save_root_path
    save_root_path = save_root_path or os.getcwd()

    sakai = Sakai()
    sites = sakai.get_site_collection()
    tasks = []
    for site in sites:
        contents = sakai.get_contents(site.id, site.title)
        for content in contents:
            # if the type is 'collection', it is a folder. otherwise, it is a file.
            if content.type != "collection":
                task = (content, sakai.requester.cookie_jar, save_root_path)
                tasks.append(task)

    with Pool(POOL_SIZE) as pool:
        pool.map(download_process, tasks)


if __name__ == "__main__":
    main()
