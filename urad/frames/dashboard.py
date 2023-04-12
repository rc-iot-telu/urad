import typing

import numpy as np

from serial.serialutil import SerialException

from PyQt5.QtCore import QThread, QTime
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QPushButton, QTimeEdit, QVBoxLayout, QWidget
)

from urad.contrib import PlotCanvas, get_port_setting, get_scale_plot
from urad.radar import URadRadar


class DashboardFrame(QWidget):
    def __init__(self, parent: typing.Optional['QWidget'] = None) -> None:
        super().__init__(parent)

        layout = QGridLayout(self)

        layout.addWidget(self._side_bar(), 0, 0, 2, 1)
        layout.addWidget(self._plot_phase_group(), 0, 1)
        layout.addWidget(self._plot_magnitude_group(), 1, 1)

        layout.setColumnStretch(0, 5)
        layout.setColumnStretch(1, 35)

        self.setLayout(layout)
        self.setStyleSheet(
            """
            QPushButton {
                border: 0;
                background: #FFF;
                color: black;
            }
            QPushButton:hover {
                background: #F7F7F7;
            }
            QPushButton:pressed  {
                background: #FFF;
            }
            """
        )

    def _side_bar(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()

        logo = QLabel(widget)
        logo.setPixmap(QPixmap("./urad/asset/logo.png"))
        logo.setScaledContents(True)

        self.start_button = QPushButton("Start Radar", widget)
        stop_button = QPushButton("Stop Radar", widget)
        save_button = QPushButton("Simpan Data", widget)

        self.timer_input = QTimeEdit()
        self.timer_input.setDisplayFormat("hh.mm.ss")

        layout.addWidget(logo)
        layout.addStretch(1)
        layout.addWidget(self.start_button)
        layout.addWidget(stop_button)
        layout.addWidget(save_button)
        layout.addWidget(self.timer_input)
        layout.addStretch(20)

        self.start_button.clicked.connect(self._start_radar)
        stop_button.clicked.connect(self._stop_radar)

        widget.setLayout(layout)
        widget.setObjectName("sideBar")
        widget.setStyleSheet(
            """
            QWidget#sideBar {
                background: #e9f5f3;
                border-radius: .5em;
            }
            """
        )
        return widget

    def _set_timer_countdown(self, sec_raw: int):
        mins = sec_raw // 60
        sec = sec_raw % 60
        hours = mins // 60
        mins = mins % 60

        self.timer_input.setTime(QTime(hours, mins, sec))

    def _start_radar(self):
        urad_port, ultrasonic_port = get_port_setting()
        timep = self.timer_input.time()

        timer_sec = (timep.hour() * 3600) + (timep.minute() * 60) + timep.second()

        try:
            self.urad_radar = URadRadar(urad_port, ultrasonic_port, timer_sec)
        except SerialException:
            print("Tidak dapat menemukan radar, pastikan port telah benar.")
            return

        self.radar_thread = QThread()

        self.urad_radar.moveToThread(self.radar_thread)
        self.radar_thread.started.connect(self.urad_radar.run)
        self.urad_radar.finished.connect(self.radar_thread.quit)
        self.urad_radar.finished.connect(self.urad_radar.deleteLater)
        self.radar_thread.finished.connect(self.radar_thread.deleteLater)

        # connect signal for radar data
        self.urad_radar.phase_plot.connect(self._plot_phase)
        self.urad_radar.magnitude_data.connect(self._plot_magnitude)

        # connect signal for gui
        self.urad_radar.time.connect(self._set_timer_countdown)
        self.urad_radar.finished.connect(self._stop_radar)

        self.radar_thread.start()
        self.start_button.setEnabled(False)

    def _stop_radar(self):
        try:
            self.urad_radar.is_taking_data = False
        except AttributeError:
            pass

        self.start_button.setEnabled(True)

    def _save_data(self):
        pass

    def _plot_phase_group(self) -> QWidget:
        widget = QGroupBox()
        layout = QHBoxLayout()

        self.phase_plot = PlotCanvas()

        layout.addWidget(self.phase_plot)

        widget.setTitle("Phase")
        widget.setLayout(layout)
        return widget

    def _plot_phase(self, phase_data: np.ndarray) -> None:
        #  refresh and plot the data
        self.phase_plot.axes.clear()

        phase_max, phase_min, _, _ = get_scale_plot()

        self.phase_plot.axes.plot(phase_data)
        self.phase_plot.axes.set_ylim([phase_min, phase_max])

        # refresh canvas
        self.phase_plot.draw_idle()
        self.phase_plot.flush_events()

    def _plot_magnitude(self, magnitude_data: np.ndarray) -> None:
        self.magnitude_plot.axes.clear()

        _, _, mag_max, mag_min = get_scale_plot()

        self.magnitude_plot.axes.plot(magnitude_data)
        self.magnitude_plot.axes.set_ylim([mag_max, mag_min])

        # refresh canvas
        self.magnitude_plot.draw_idle()
        self.magnitude_plot.flush_events()

    def _plot_magnitude_group(self) -> QWidget:
        widget = QGroupBox()
        layout = QHBoxLayout()

        self.magnitude_plot = PlotCanvas()

        layout.addWidget(self.magnitude_plot)

        widget.setTitle("Magnitude")
        widget.setLayout(layout)
        return widget
