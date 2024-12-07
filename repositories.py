import pathlib
import json

from datetime import datetime, timezone


STORAGE_PATH = pathlib.Path().joinpath("storage")


class FileRepository:
    def __init__(self, file_name):
        self.data_path = STORAGE_PATH / file_name

    def _read_json(self):
        with open(self.data_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def _write_json(self, data):
        with open(self.data_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)


class MessagesRepository(FileRepository):
    def __init__(self):
        super().__init__("messages.json")

    def get_all(self):
        return self._read_json()

    def create(self, message):
        saved_messages = self.get_all()
        timestamp = datetime.now(timezone.utc).isoformat()
        saved_messages[timestamp] = message
        self._write_json(saved_messages)


class CoursesRepository(FileRepository):
    def __init__(self):
        super().__init__("courses.json")

    def get_all(self):
        return self._read_json() or []


messages_repository = MessagesRepository()
courses_repository = CoursesRepository()
