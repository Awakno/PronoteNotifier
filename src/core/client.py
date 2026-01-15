import pronotepy
from datetime import datetime, timedelta


class Client:
    def __init__(self, url: str, username: str, password: str) -> None:
        self.client: pronotepy.Client = pronotepy.Client(
            url,
            username,
            password,
            uuid="PronoteNotifierV2",
            device_name="PronoteNotifier",
        )
        self.connected: bool = False
        if self.client.logged_in:
            self.connected: bool = True

    def logout(self) -> bool:
        if self.connected:
            self.client.logout()
            self.connected = False
            return True
        return False

    def keep_alive(self) -> None:
        if self.connected:
            self.client.keep_alive()

    def is_connected(self) -> bool:
        return self.connected

    def keep_connection_alive(self) -> None:
        self.client = self.client.refresh(self.client)

    def get_homework(self) -> list[pronotepy.Homework]:
        if not self.connected:
            return []

        return self.client.homework(
            date_from=datetime.now().date(),
            date_to=(datetime.now() + timedelta(days=14)).date(),
        )

    def get_grades(self) -> list[pronotepy.Grade]:
        if not self.connected:
            return []
        grades: list[pronotepy.Grade] = []

        for period in self.client.periods:
            for grade in period.grades:
                grades.append(grade)

        return grades
