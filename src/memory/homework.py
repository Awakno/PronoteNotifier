from datetime import datetime, timedelta
import pronotepy


class HomeworkManager:
    def __init__(self, client: pronotepy.Client) -> None:
        self.client: pronotepy.Client = client
        self._cache_homework: list[pronotepy.Homework] = []

    def get_homework(self) -> list[pronotepy.Homework]:
        return self._cache_homework

    def update_homework(self) -> None:
        self._cache_homework = self.client.homework(
            date_from=datetime.now().date(),
            date_to=(datetime.now() + timedelta(days=14)).date(),
        )

    def clear_homework(self) -> None:
        self._cache_homework = []

    def has_homework(self) -> bool:
        return len(self._cache_homework) > 0

    def add_homework(self, homework: pronotepy.Homework) -> None:
        self._cache_homework.append(homework)

    def remove_homework(self, homework: pronotepy.Homework) -> None:
        self._cache_homework.remove(homework)

    def find_homework_by_id(self, homework_id: str) -> pronotepy.Homework | None:
        for homework in self._cache_homework:
            if homework.id == homework_id:
                return homework
        return None

    def find_homework_by_subject(self, subject: str) -> list[pronotepy.Homework]:
        result: list[pronotepy.Homework] = []
        for homework in self._cache_homework:
            if homework.subject == subject:
                result.append(homework)
        return result

    def find_homework_by_date(self, date: str) -> list[pronotepy.Homework]:
        result: list[pronotepy.Homework] = []
        for homework in self._cache_homework:
            if homework.date == date:
                result.append(homework)
        return result

    def clear_old_homework(self, date: str) -> None:
        self._cache_homework = [hw for hw in self._cache_homework if hw.date >= date]
