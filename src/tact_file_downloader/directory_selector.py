import tkinter as tk
from tkinter import filedialog
import configparser
import os


class DirectorySelector:
    def __init__(self) -> None:
        current_dir = os.path.dirname(__file__)
        grandparent_dir = os.path.dirname(os.path.dirname(current_dir))
        self.config_path = os.path.join(grandparent_dir, "config.ini")
        if not os.path.exists(self.config_path):
            with open(self.config_path, "w") as _:
                pass
        self.save_root_path = self.__get_save_root_path()

    def __select_directory(self) -> str:
        print("ダウンロード先のディレクトリを選択してください。")
        root = tk.Tk()
        root.withdraw()
        directory = filedialog.askdirectory()
        return directory

    def __get_save_root_path(self) -> str:
        config = configparser.ConfigParser()
        config.read(self.config_path)

        if "Default" not in config:
            config.add_section("Default")

        save_root_path = config.get("Default", "save_root_path", fallback="null")

        if save_root_path.lower() in ["null", "none", ""]:
            new_save_root_path = self.__select_directory()
            if new_save_root_path == "":
                raise ValueError("ディレクトリが選択されませんでした。")
            self.__update_config(
                config, "Default", "save_root_path", new_save_root_path
            )
            return new_save_root_path

        return save_root_path

    def __update_config(
        self, config: configparser.ConfigParser, section: str, key: str, value: str
    ) -> None:
        config.set(section, key, value)

        with open(self.config_path, "w") as config_file:
            config.write(config_file)


if __name__ == "__main__":
    d = DirectorySelector()
    print(d.save_root_path)
