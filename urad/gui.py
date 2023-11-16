import typing
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QDesktopWidget, QMainWindow, QMenuBar, QWidget
)

from urad.dialogs import SettingDialog
from urad.frames import DashboardFrame


class MainWindow(QMainWindow):
    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Urad Radar")
        self.setWindowIcon(QIcon("./urad/asset/radar.png"))
        self._create_menubar()

        self.setCentralWidget(DashboardFrame())

    def show(self) -> None:
        self._center_window()
        return super().show()

    def _center_window(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def _open_setting(self):
        SettingDialog(self).exec()

    def _create_menubar(self):
        menubar = QMenuBar()


        app_menu = menubar.addMenu("&Aplikasi")

        app_menu.addAction("Pengaturan")
        app_menu.addAction("Keluar")

        app_menu.actions()[0].triggered.connect(self._open_setting)
        app_menu.actions()[1].triggered.connect(sys.exit)

        menubar.setStyleSheet(
            """
            QMenuBar {
                background: #f2eae1;
                border: 0;
            }
            """
        )
        self.setMenuBar(menubar)
