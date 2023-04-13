import time
import os
import json

from serial.tools.list_ports import comports

from PyQt5.QtCore import QThread, pyqtSignal
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#  from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as PlotNavBar


def list_com_port(get_first_port: bool = False) ->  str:
    """
    Scan all COM port available on the device,
    and return it as a string
    """
    ports = comports()

    if not ports:
        return "Tidak ada perangkat yang terhubung!"

    ports = ["{}: {} [{}]\n".format(port, desc, hwid) for port, desc, hwid in sorted(ports)]
    ports = "".join(ports)

    if not get_first_port:
        return ports

    return ports.split(":")[0]

def get_scale_plot():
    """
    Read data for the default value: application setting
    """
    file_path = "./urad/dialogs"
    try:
        with open(os.path.join(file_path, "settings.json"), "r") as f:
            setting_data: dict = json.loads(f.read())

            phase_max = setting_data.get("phase_max")
            phase_min = setting_data.get("phase_min")
            mag_max = setting_data.get("mag_max")
            mag_min = setting_data.get("mag_min")

            return phase_max, phase_min, mag_max, mag_min

    except FileNotFoundError:
        return ""


def get_port_setting():
    """
    Read data for the default value: application setting
    """
    file_path = "./urad/dialogs"
    try:
        with open(os.path.join(file_path, "settings.json"), "r") as f:
            setting_data: dict = json.loads(f.read())

            urad_port = str(setting_data.get("urad_port"))
            ultrasonik_port = str(setting_data.get("ultrasonik_port"))

            return urad_port, ultrasonik_port

    except FileNotFoundError:
        return ""

def get_path_setting():
    """
    Read data for the default value: application setting
    """
    file_path = "./urad/dialogs"
    try:
        with open(os.path.join(file_path, "settings.json"), "r") as f:
            setting_data: dict = json.loads(f.read())

            path_setting = str(setting_data.get("dir_path"))

            return path_setting

    except FileNotFoundError:
        return ""

class Timer(QThread):
    time_lapsed = pyqtSignal(str)
    time_lapsed_sec = pyqtSignal(int)

    def __init__(self, sec_raw) -> None:
        QThread.__init__(self)

        self.start_ticking = True
        self.pause_ticking = False
        self.sec_remain = sec_raw

    def _convert_time(self, sec_raw):
        mins = sec_raw // 60
        sec = sec_raw % 60
        hours = mins // 60
        mins = mins % 60

        self.time_lapsed_sec.emit(sec_raw)
        self.time_lapsed.emit(f"{int(hours):02}:{int(mins):02}:{int(sec):02}")

    def stop(self):
        self.start_ticking = False

    def run(self) -> None:
        self.start_ticking = True
        while self.start_ticking:

            if self.pause_ticking:
                continue

            self.sec_remain -= 1
            self._convert_time(self.sec_remain)
            time.sleep(1)

class PlotCanvas(FigureCanvas):
    def __init__(self) -> None:
        self.figure = Figure(tight_layout=True)
        self.figure.subplots_adjust(hspace=0)

        self.axes = self.figure.add_subplot(111)
        super(PlotCanvas, self).__init__(self.figure)

