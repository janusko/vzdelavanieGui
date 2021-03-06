from PyQt5.QtCore import QFileInfo, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QFileIconProvider, QTreeWidgetItem

from vgrabber.model.files import StoredFile, ExternalFile
from ..items import FileItem

fip = QFileIconProvider()


def add_file_items(files, parent_item: QTreeWidgetItem):
    for file in files:
        file_item = FileItem([file.file_name], file)
        file_item.setIcon(0, fip.icon(QFileInfo(file.file_name)))
        parent_item.addChild(file_item)
        file_item.setFirstColumnSpanned(True)


def file_double_clicked(model, item):
    if isinstance(item, FileItem) and isinstance(item.file, (StoredFile, ExternalFile)):
        file_path = model.data_layer.open_file_for_external_app(item.file.file_path)
        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
