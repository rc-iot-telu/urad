import os
import json
import typing

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QWidget, 
    QGroupBox, QLineEdit, QPushButton,
    QTextEdit, QVBoxLayout
)

from urad.contrib import list_com_port


class SettingDialog(QDialog):
    def __init__(self, parent: typing.Optional[QWidget]) -> None:
        super().__init__(parent)
        self.setWindowTitle("Pengaturan Port")

        setting = self._read_setting()

        self.urad_port = str(setting.get("urad_port"))
        self.ultrasonik_port = str(setting.get("ultrasonik_port"))
        self.dir_path = str(setting.get("dir_path"))

        self.phase_max = str(setting.get("phase_max"))
        self.phase_min = str(setting.get("phase_min"))

        self.mag_max = str(setting.get("mag_max"))
        self.mag_min = str(setting.get("mag_min"))

        layout = QVBoxLayout()
        layout.addWidget(self._form_group())

        self.setLayout(layout)

    def _folder_selected(self, selected_dir):
        self.dir_path = str(selected_dir)

    def _form_group(self):
        group_box = QGroupBox(self)
        layout = QFormLayout()

        urad_port = QLineEdit(self.urad_port, group_box)
        ultrasonik_port = QLineEdit(self.ultrasonik_port, group_box)

        phase_max = QLineEdit(self.phase_max, group_box)
        phase_min = QLineEdit(self.phase_min, group_box)

        mag_max = QLineEdit(self.mag_max, group_box)
        mag_min = QLineEdit(self.mag_min, group_box)

        urad_port_list = QTextEdit(list_com_port(), group_box)
        save_button = QPushButton("Simpan Pengaturan", group_box)
        refresh_button = QPushButton("Refresh Daftar Port", group_box)

        layout.addRow("Port URad", urad_port)
        layout.addRow("Port Ultrasonik", ultrasonik_port)
        layout.addRow(QWidget())
        layout.addRow("Max Plot Phasa", phase_max)
        layout.addRow("Min Plot Phasa", phase_min)
        layout.addRow(QWidget())
        layout.addRow("Max Plot Mag", mag_max)
        layout.addRow("Min Plot Mag", mag_min)
        layout.addRow(QWidget())
        layout.addRow(urad_port_list)
        layout.addRow(save_button)
        layout.addRow(refresh_button)

        def save_port():
            self.urad_port = urad_port.text()
            self.ultrasonik_port = ultrasonik_port.text()
            self.phase_max = float(phase_max.text())
            self.phase_min = float(phase_min.text())
            self.mag_max = float(mag_max.text())
            self.mag_min = float(mag_min.text())

            self._save_setting()

        def refresh_fmcw_list():
            port_list = list_com_port()
            urad_port_list.setText(port_list)

            # we assume no devices connected
            if port_list == "Tidak ada perangkat yang terhubung!":
                return

            for port in port_list.split("\n"):
                p = port.split(":")
                if len(p) < 2 or not p[1].startswith(" USB Serial Device"):
                    continue

                port_number = p[0]
                self.urad_port = port_number
                urad_port.setText(port_number)
                break

            self._save_setting()

        save_button.clicked.connect(save_port)
        refresh_button.clicked.connect(refresh_fmcw_list)

        group_box.setLayout(layout)
        return group_box

    def _read_setting(self) -> dict:
        """
        Read data for the default value: application setting
        """
        file_path = os.path.dirname(os.path.realpath(__file__))
        try:
            with open(os.path.join(file_path, "settings.json"), "r") as f:
                return json.loads(f.read())
        except FileNotFoundError:
            return {}

    def _save_setting(self):
        setting = {
            "urad_port": self.urad_port,
            "ultrasonik_port": self.ultrasonik_port,
            "dir_path": self.dir_path,
            "phase_max": self.phase_max,
            "phase_min": self.phase_min,
            "mag_max": self.mag_max,
            "mag_min": self.mag_min,
        }

        file_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(file_path, "settings.json"), "w") as f:
            f.write(json.dumps(setting))
