from dataclasses import dataclass


@dataclass
class SakaiContent:
    container: str  # "\/content\/group\/{site_id}\/{directory_name}\/{sub_directory_name_and_so_on}",
    title: str
    type: str # if type is "container" then it is a directory. otherwise it is a file
    url: str
    site_title: str

    def __post_init__(self):
        path_parts = self.container.split("/")
        path_parts[2] = self.site_title # replace the site_id with the site_title
        self.path = "/".join(path_parts[2:]) # remove the first two parts of the path
