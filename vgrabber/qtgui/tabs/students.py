from urllib.parse import urlencode

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QSplitter, QMenu

from vgrabber.model import Student
from vgrabber.qtgui.tabs.widgets.filedetails import FileDetailsWidget
from .helpers.childfileitems import add_file_items, file_double_clicked
from .helpers.stringify import points_or_none, grade_or_none
from .items import StudentItem
from ..guimodel import GuiModel


class StudentsTab:
    model: GuiModel

    def __init__(self, model):
        self.__student_list = QTreeWidget()
        self.__student_list.setSortingEnabled(True)
        self.__student_list.setColumnCount(5)
        self.__student_list.setHeaderLabels(["Number", "Full Name", "Group", "Moodle email", "Moodle group", "Semestral points"])
        self.__student_list.itemSelectionChanged.connect(self.__student_selected)
        self.__student_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.__student_list.customContextMenuRequested.connect(self.__student_list_context_menu)
        self.__student_list.setSelectionMode(QTreeWidget.ExtendedSelection)

        self.__student_details = QTreeWidget()
        self.__student_details.setColumnCount(4)
        self.__student_details.setHeaderLabels(["Type", "Activity name", "Points", "Grade"])
        self.__student_details.itemActivated.connect(
            lambda item, column: file_double_clicked(self.model, item)
        )
        self.__student_details.itemSelectionChanged.connect(self.__student_file_selected)

        self.__student_file_details = FileDetailsWidget(model)

        details_splitter = QSplitter(Qt.Horizontal)
        details_splitter.addWidget(self.__student_details)
        details_splitter.addWidget(self.__student_file_details.widget)

        self.widget = QSplitter(Qt.Vertical)
        self.widget.addWidget(self.__student_list)
        self.widget.addWidget(details_splitter)
        self.widget.setStretchFactor(0, 3)
        self.widget.setStretchFactor(1, 1)

        self.model = model
        self.__load_students()

        self.model.subject_changed.connect(self.__subject_changed)
    
    @property
    def headers(self):
        hdr = self.__student_list.headerItem()
        return [hdr.text(i) for i in range(hdr.columnCount())]
    
    @property
    def data(self):
        for no in range(self.__student_list.topLevelItemCount()):
            item = self.__student_list.topLevelItem(no)
            ret = [item.text(i) for i in range(item.columnCount())]
            yield ret

    def __subject_changed(self):
        self.__load_students()

    def __load_students(self):
        self.__student_list.clear()
        self.__student_details.clear()

        if self.model.subject is not None:
            for student in self.model.subject.students:
                moodle_group = student.get_moodle_group()
                moodle_group_name = ""
                if moodle_group is not None:
                    moodle_group_name = moodle_group.moodle_name

                item = StudentItem(
                    [
                        student.number,
                        f"{student.surname} {student.name}",
                        student.group,
                        student.moodle_email,
                        moodle_group_name,
                        str(student.compute_semestral_grading())
                    ],
                    student
                )
                self.__student_list.addTopLevelItem(item)

    def __student_selected(self):
        self.__student_details.clear()

        student_items = self.__student_list.selectedItems()
        if student_items:
            student: Student = student_items[0].student
            for homework_points in student.home_work_points:
                homework_item = QTreeWidgetItem([
                    "Home Work",
                    homework_points.home_work.name,
                    points_or_none(homework_points.points),
                    ""
                ])
                self.__student_details.addTopLevelItem(homework_item)
                add_file_items(homework_points.files, homework_item)

            for test_points in student.test_points:
                test_item = QTreeWidgetItem([
                    "Test",
                    test_points.test.name,
                    points_or_none(test_points.points),
                    ""
                ])
                self.__student_details.addTopLevelItem(test_item)
                add_file_items(test_points.files, test_item)

            for grade in student.grades:
                grade_item = QTreeWidgetItem([
                    "Final Exam",
                    grade.final_exam.date_time.strftime("%c"),
                    points_or_none(grade.points),
                    grade_or_none(grade.grade)
                ])
                self.__student_details.addTopLevelItem(grade_item)
                add_file_items(grade.files, grade_item)

        self.__student_details.expandAll()

    def __student_file_selected(self):
        self.__student_file_details.master_selection_changed(
            self.__student_details.selectedItems()
        )

    def __student_list_context_menu(self, pos):
        menu = QMenu()
        menu.addAction("Send mail").triggered.connect(
            lambda *args: self.__send_mail_to_selected()
        )
        menu.exec(self.__student_list.viewport().mapToGlobal(pos))
    
    def __send_mail_to_selected(self):
        mails = []
        for student_item in self.__student_list.selectedItems():
            if isinstance(student_item, StudentItem):
                mails.append("{0} {1} <{2}>".format(student_item.student.name, student_item.student.surname, student_item.student.moodle_email))
        
        mailtourl = {'to': ','.join(mails)}
        QDesktopServices.openUrl(QUrl("mailto:?" + urlencode(mailtourl).replace('+', '%20'), QUrl.TolerantMode))
