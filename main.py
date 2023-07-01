"""
        Helper_Bot
"""
import datetime
import json
import os
from abc import ABC

from telebot import TeleBot, types


class File(ABC):
    def __init__(self):
        self.header = ""

    def get_header_file(self, name):
        pass

    @staticmethod
    def check_file(path):
        type_file = path.split(".")[-1]
        if type_file == "py":
            return PythonFile().get_header_file(path)
        elif type_file == "ipynb":
            return IPythonFile().get_header_file(path)
        elif type_file == "info":
            return InfoFile().get_header_file(path)
        else:
            raise ValueError("UNKNOWN TYPE OF FILE")


class PythonFile(File):
    def get_header_file(self, name):
        with open(name, "r") as f:
            f.readline()
            for row in f.readlines():
                if '"""' in row:
                    break
                self.header = self.header + row + "\n"
            return self.header


class InfoFile(File):
    def get_header_file(self, name):
        with open(name, "r") as f:
            for row in f.readlines():
                self.header = self.header + row + "\n"
            return self.header


class IPythonFile(File):
    def get_header_file(self, name):
        type_file = name.split(".")[-1]
        name = name.replace(f".{type_file}", ".txt")
        with open(name, "r") as f:
            for row in f.readlines():
                self.header = self.header + row + "\n"
            return self.header


class Bot_Helper:
    TOKEN = ""
    CHANNEL = ""
    ID_ADMIN = 0
    def __init__(self, path):
        self.bot = TeleBot(token=self.TOKEN)
        self.path = path
        """ПРОБЛЕМА?"""
        # self.bot.infinity_polling(interval=0,timeout=20)

    def send_need_files(self):
        for filename in next(os.walk(self.path))[2]:
            if ".py" in filename or ".ipynb" in filename or ".info" in filename:
                self.send_doc(f"{self.path}/{filename}")

    def send_doc(self, name):
        try:
            doc = open(name, 'rb')
            if name not in self.get_all_records_name():
                message_log = self.bot.send_document(chat_id=self.CHANNEL, document=doc,
                                                     caption=self.get_header_file(name))
                self.adding_log(name)
                print(message_log)
                text_to_admin = f"Запись '{name}' добавлена от {datetime.datetime.utcfromtimestamp(message_log.date).strftime('%Y-%m-%d %H:%M:%S')}"
                self.bot.send_message(chat_id=self.ID_ADMIN, text=text_to_admin)
            else:
                print("suwestviet")
        except Exception as e:
            text_to_admin = f"Запись '{name}' не добавлена из за {e}"
            self.bot.send_message(chat_id=self.ID_ADMIN, text=text_to_admin)
            self.send_doc_big_header()
        finally:
            doc.close()

    @staticmethod
    def get_header_file(name):
        return File.check_file(name)

    @staticmethod
    def adding_log(name):
        with open("log", "a+") as f:
            json_record = '{"name": "%s"}\n' % name
            f.write(json_record)

    @staticmethod
    def get_all_records_name():
        list_name = []
        if os.path.exists("log"):
            with open("log", "r") as f:
                for row in f.readlines():
                    list_name.append(json.loads(row)['name'])
        return list_name

    def send_doc_big_header(self):  # отправка заголовка c файлом если он больше 500 символов
        pass


if __name__ == "__main__":
    name_dir = "patterns"
    bot_helper = Bot_Helper(f"/home/alex/PycharmProjects/proj_for_bot/{name_dir}")
    bot_helper.send_need_files()
