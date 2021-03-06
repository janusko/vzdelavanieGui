import csv
from os.path import dirname, basename, isdir
from traceback import format_exc, print_exc
from typing import List

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import QMainWindow, QMenuBar, QTabWidget, QApplication, QFileDialog, QMessageBox

from vgrabber.base.importaction import ImportAction
from vgrabber.base.exportaction import ExportAction
from vgrabber.datalayer.fileaccessors import DirectoryFileAccessor, ZipFileAccessor
from .tabs import StudentsTab, TeachersTab, HomeWorksTab, TestsTab, FinalExamsTab

try:
    from vgrabber.syncer import Importer, Exporter
    from vgrabber.qtgui.syncing import LoginDialog, SyncSelectorDialog, QtCallbacks

    ALLOW_SYNC = True
except ImportError:
    print_exc()
    ALLOW_SYNC = False


class MainWindow:
    def __init__(self, model):
        self.model = model
        self.__tabs = []  # keeps references to tab instances

        self.__window = QMainWindow()
        self.__set_title()
        self.__window.setMinimumSize(600, 600)
        self.__build_menu()
        self.__build_tabs()
        self.__refresh_recents()
        self.__subject_changed()

        self.model.subject_changed.connect(self.__subject_changed)

    def __build_menu(self):
        menu_bar = QMenuBar()
        
        file_menu = menu_bar.addMenu("File")
        self.__open_action = file_menu.addAction("Open...")
        self.__open_action.triggered.connect(self.__open_clicked)
        self.__recent_menu = file_menu.addMenu("Recent files")
        self.__save_action = file_menu.addAction("Save")
        self.__save_action.triggered.connect(self.__save_clicked)
        self.__save_as_action = file_menu.addAction("Save as...")
        self.__save_as_action.triggered.connect(self.__save_as_clicked)
        self.__close_action = file_menu.addAction("Close")
        self.__close_action.triggered.connect(self.__close_clicked)
        file_menu.addSeparator()
        self.__exit_action = file_menu.addAction("Exit")
        self.__exit_action.triggered.connect(self.__exit_clicked)
        
        sync_menu = menu_bar.addMenu("Sync")
        self.__import_action = sync_menu.addAction("Import...")
        self.__import_action.triggered.connect(self.__import_clicked)
        self.__export_action = sync_menu.addAction("Export...")
        self.__export_action.triggered.connect(self.__export_clicked)
        
        tab_menu = menu_bar.addMenu("Tab")
        self.__export_csv_action = tab_menu.addAction("Export CSV...")
        self.__export_csv_action.triggered.connect(self.__export_csv_clicked)
        
        self.__window.setMenuBar(menu_bar)

    def __build_tabs(self):
        def add_tab(tab_class, label):
            tab = tab_class(self.model)
            self.__tabs.append(tab)
            self.__tabWidget.addTab(tab.widget, label)

        self.__tabWidget = QTabWidget()
        self.__tabWidget.setEnabled(False)

        add_tab(StudentsTab, "Students")
        add_tab(TeachersTab, "Teachers")
        add_tab(HomeWorksTab, "Home works")
        add_tab(TestsTab, "Tests")
        add_tab(FinalExamsTab, "Final exams")

        self.__tabWidget.currentChanged.connect(lambda *args: self.__refresh_menu_enabled())
        
        self.__window.setCentralWidget(self.__tabWidget)

    def __subject_changed(self):
        self.__set_title()
        
        self.__refresh_menu_enabled()

        has_model = self.model.subject is not None

        self.__tabWidget.setEnabled(has_model)
    
    def __refresh_menu_enabled(self):
        has_model = self.model.subject is not None
    
        self.__save_action.setEnabled(has_model and self.model.data_layer.can_save)
        self.__save_as_action.setEnabled(has_model)
        self.__close_action.setEnabled(has_model)
    
        self.__import_action.setEnabled(ALLOW_SYNC)
        self.__export_action.setEnabled(ALLOW_SYNC and has_model)
    
        self.__export_csv_action.setEnabled(has_model and self.__can_export_csv())

    def __set_title(self):
        if self.model.subject is None:
            self.__window.setWindowTitle("Vzdelavanie GUI")
        else:
            self.__window.setWindowTitle("Vzdelavanie GUI ({0} {1} {2})".format(
                self.model.subject.number,
                self.model.subject.name,
                self.model.subject.year
            ))
    
    def __export_clicked(self, *args):
        self.__do_sync(ExportAction, Exporter)
    
    def __import_clicked(self, *args):
        self.__do_sync(ImportAction, Importer)
    
    def __do_sync(self, actions_enum, syncer):
        login_dlg = LoginDialog()
        login, password = login_dlg.exec()

        if login is None:
            return

        if self.model.subject is not None:
            finished_actions = self.model.subject.progress
        else:
            finished_actions = []

        import_dlg = SyncSelectorDialog(actions_enum, finished_actions)
        actions = import_dlg.exec()
        if actions is None:
            return

        with syncer(login, password, actions, QtCallbacks(), self.model.subject) as syncer_obj:
            syncer_obj.exec()
            self.model.use_subject(syncer_obj.model)

    def __open_clicked(self, *args):
        file_name, filter = QFileDialog.getOpenFileName(
            self.__window,
            caption="Open Data",
            filter="Imported data (subjectinfo.xml);;Zipped imported data (*.zip)"
        )

        if file_name:
            if 'zip' in filter:
                accessor = ZipFileAccessor(file_name)
                self.__add_current_file(file_name)
            else:
                dir_name = dirname(file_name)
                accessor = DirectoryFileAccessor(dir_name)
                self.__add_current_file(dir_name)

            try:
                self.model.load(accessor)
            except Exception:
                print_exc()
                exc = format_exc()
                message_box = QMessageBox(self.__window)
                message_box.setWindowModality(Qt.WindowModal)
                message_box.setIcon(QMessageBox.Critical)
                message_box.setWindowTitle("Error deserializing")
                message_box.setText(exc)
                message_box.exec()

    def __save_clicked(self, *args):
        self.model.save()

    def __save_as_clicked(self, *args):
        file_name, filter = QFileDialog.getSaveFileName(
            self.__window,
            caption="Save Data",
            filter="Imported data (subjectinfo.xml);;Zipped imported data (*.zip)"
        )

        if file_name:
            if 'zip' in filter:
                accessor = ZipFileAccessor(file_name)
                self.__add_current_file(file_name)
            else:
                dir_name = dirname(file_name)
                self.__add_current_file(dir_name)
                accessor = DirectoryFileAccessor(dir_name)
            self.model.save_as(accessor)

    def __close_clicked(self, *args):
        self.model.use_subject(None)

    def __exit_clicked(self, *args):
        QApplication.exit(0)
    
    def __can_export_csv(self):
        current_tab = self.__get_current_tab()
        return 'data' in dir(current_tab) and 'headers' in dir(current_tab)
    
    def __export_csv_clicked(self, *args):
        if self.__can_export_csv:
            file_name, filter = QFileDialog.getSaveFileName(
                self.__window,
                caption="Export CSV",
                filter="CSV (*.csv)"
            )
    
            if file_name:
                if '.' not in basename(file_name):
                    file_name = file_name + '.csv'
                current_tab = self.__get_current_tab()
                with open(file_name, 'w') as csv_file:
                    csv_obj = csv.writer(csv_file)
                    csv_obj.writerow(current_tab.headers)
                    for row in current_tab.data:
                        csv_obj.writerow(row)

    def __add_current_file(self, file):
        settings = QSettings()
        recentFileList: List[str] = settings.value("recentFileList", defaultValue=[])
        if file in recentFileList:
            recentFileList.remove(file)
        recentFileList.insert(0, file)
        settings.setValue("recentFileList", recentFileList)
        self.__refresh_recents()

    def show(self):
        self.__window.showMaximized()

    def __refresh_recents(self):
        settings = QSettings()
        recentFileList: List[str] = settings.value("recentFileList", defaultValue=[])
        self.__recent_menu.clear()
        for file in recentFileList:
            action = self.__recent_menu.addAction(basename(file))
            self.__connect_recent_menu_action(action, file)

    def __connect_recent_menu_action(self, action, file):
        def open():
            if isdir(file):
                accessor = DirectoryFileAccessor(file)
            else:
                accessor = ZipFileAccessor(file)
            self.model.load(accessor)
            self.__add_current_file(file)
        action.triggered.connect(open)
    
    def __get_current_tab(self):
        return self.__tabs[self.__tabWidget.currentIndex()]

