import pronotepy


class GradeManager:
    def __init__(self, client: pronotepy.Client) -> None:
        self.client: pronotepy.Client = client
        self._cache_grades: list[pronotepy.Grade] = []

    def get_grades(self) -> list[pronotepy.Grade]:
        return self._cache_grades

    def update_grades(self) -> None:
        grades: list[pronotepy.Grade] = []
        for period in self.client.periods:
            for grade in period.grades:
                grades.append(grade)
        self._cache_grades = grades

    def clear_grades(self) -> None:
        self._cache_grades = []

    def has_grades(self) -> bool:
        return len(self._cache_grades) > 0

    def add_grade(self, grade: pronotepy.Grade) -> None:
        self._cache_grades.append(grade)

    def remove_grade(self, grade: pronotepy.Grade) -> None:
        self._cache_grades.remove(grade)

    def find_grade_by_id(self, grade_id: str) -> pronotepy.Grade | None:
        for grade in self._cache_grades:
            if grade.id == grade_id:
                return grade
        return None

    def find_grades_by_subject(self, subject: str) -> list[pronotepy.Grade]:
        result: list[pronotepy.Grade] = []
        for grade in self._cache_grades:
            if grade.subject == subject:
                result.append(grade)
        return result

    def estimate_average(self) -> float | None:
        if not self._cache_grades or len(self._cache_grades) == 0:
            return None

        total: float = 0.0
        for grade in self._cache_grades:
            total += grade.value

        return total / len(self._cache_grades)

    def average_by_subject(self, subject: str) -> float | None:
        subject_grades: list[pronotepy.Grade] = self.find_grades_by_subject(subject)
        if not subject_grades or len(subject_grades) == 0:
            return None

        total: float = 0.0
        for grade in subject_grades:
            total += grade.value

        return total / len(subject_grades)
