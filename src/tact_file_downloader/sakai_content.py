from dataclasses import dataclass


@dataclass
class SakaiContent:
    container: str  # "\/content\/group\/{site_id}\/{directory_name}\/{sub_directory_name_and_so_on}",
    title: str
    type: str  # if type is "container" then it is a directory. otherwise it is a file
    url: str
    site_title: str
    is_site_root: bool = False

    def __post_init__(self) -> None:
        path_parts = self.container.split("/")
        path_parts = list(filter(lambda x: x != "", path_parts))
        # '/' is not allowed in file name.
        self.title = self.title.replace("/", "_")
        self.site_title = self.site_title.replace("/", "_")
        # replace the site_id with the site_title. if the Content is the root directory of the site, the path_parts will be less than 3.
        if len(path_parts) > 2:
            path_parts[2] = self.site_title
        else:
            self.is_site_root = True
        self.path = "/".join(path_parts[2:])  # remove the first two parts of the path
