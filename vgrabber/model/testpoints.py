from .files import FileList
from .test import Test


class TestPoints:
    test: Test
    points: float
    files: FileList

    def __init__(self, subject, student, test, points):
        self.__subject = subject
        self.test = test
        self.points = points
        self.files = FileList()

        self.student = student

    def clear_files(self):
        self.files.clear()
