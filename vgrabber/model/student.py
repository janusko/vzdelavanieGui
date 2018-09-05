import os.path
from typing import List

from vgrabber.utilities.accents import strip_accents
from .grade import StudentGrade
from .homeworkpoints import HomeWorkPoints
from .testpoints import TestPoints


class Student:
    number: str
    name: str
    surname: str
    group: str
    grades: List[StudentGrade]
    moodle_id: int
    moodle_group_id: int
    moodle_email: str
    home_work_points: List[HomeWorkPoints]
    test_points: List[TestPoints]

    def __init__(self, subject, number, name, surname, group):
        self.__subject = subject
        self.number = number
        self.name = name
        self.surname = surname
        self.group = group
        self.grades = []
        self.moodle_id = None
        self.moodle_group_id = None
        self.moodle_email = None
        self.home_work_points = []
        self.test_points = []

    def __str__(self):
        graded = ""
        if self.grades:
            graded = ", graded {0}".format(self.grades[-1])
        return "<Student {0} {1} in group {2}, number {3}{4}>".format(
            self.name,
            self.surname,
            self.group,
            self.number,
            graded
        )

    def add_grade(self, grade):
        self.grades.append(grade)

    def add_test_points(self, test, points):
        self.test_points.append(TestPoints(self.__subject, self, test, points))

    def add_home_work_points(self, home_work, points):
        self.home_work_points.append(HomeWorkPoints(self.__subject, self, home_work, points))

    def add_final_exam_points(self, final_exam, points):
        for grade in self.grades:
            if grade.final_exam == final_exam:
                grade.points = points
                break
        else:
            grade = StudentGrade(self.__subject, self, final_exam, None)
            grade.points = points
            self.grades.append(grade)

    def add_final_exam_file(self, final_exam, file):
        for grade in self.grades:
            if grade.final_exam == final_exam:
                grade.files.add_file(file)
                break
        else:
            grade = StudentGrade(self.__subject, self, final_exam, None)
            grade.files.add_file(file)
            self.grades.append(grade)

    def add_home_work_file(self, home_work, file):
        for home_work_points in self.home_work_points:
            if home_work_points.home_work == home_work:
                home_work_points.files.add_file(file)
                break
        else:
            home_work_points = HomeWorkPoints(self.__subject, self, home_work, None)
            home_work_points.files.add_file(file)
            self.home_work_points.append(home_work_points)

    def add_test_file(self, test, file):
        for test_points in self.test_points:
            if test_points.test == test:
                test_points.files.add_file(file)
                break
        else:
            test_points = TestPoints(self.__subject, self, test, None)
            test_points.files.add_file(file)
            self.test_points.append(test_points)

    def clear_grades(self):
        self.grades.clear()

    def clear_final_exam_points(self):
        for grade in self.grades:
            grade.points = None

    def clear_home_work_points(self):
        self.home_work_points.clear()

    def clear_test_points(self):
        self.test_points.clear()

    def clear_final_exam_files(self):
        for grade in self.grades:
            grade.clear_files()

    def clear_home_work_files(self):
        for home_work_points in self.home_work_points:
            home_work_points.clear_files()

    def clear_test_files(self):
        for test_points in self.test_points:
            test_points.clear_files()

    def get_moodle_group(self):
        for teacher in self.__subject.teachers:
            for group in teacher.taught_groups:
                if group.moodle_id == self.moodle_group_id:
                    return group

    def save(self, old_file_accessor_root, file_accessor):
        student_dir = file_accessor.open_folder(
            '{0}_{1}{2}'.format(self.number, strip_accents(self.surname), strip_accents(self.name))
        )

        for grade in self.grades:
            grade.save(old_file_accessor_root, student_dir)

        for home_work_point in self.home_work_points:
            home_work_point.save(old_file_accessor_root, student_dir)

        for test_points in self.test_points:
            test_points.save(old_file_accessor_root, student_dir)
