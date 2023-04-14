import typing
import time

import serial
import numpy as np

from PyQt5.QtCore import QObject, pyqtSignal

from urad import uRAD_USB_SDK11
from urad.contrib import Timer
from urad.radar.ultrasonic import UltrasonicSensor

class URadRadar(QObject):
    # data for ploting
    phase_plot = pyqtSignal(np.ndarray)
    magnitude_plot = pyqtSignal(np.ndarray)
    time = pyqtSignal(int)

    # data that to be save
    magnitude_data = pyqtSignal(np.ndarray)
    peek_phase = pyqtSignal(float)
    i_data = pyqtSignal(np.ndarray)
    q_data = pyqtSignal(np.ndarray)
    ultrasonic_data = pyqtSignal(float)

    # system signal
    finished = pyqtSignal()

    def __init__(self,
                 urad_port: str,
                 ultrasonic_port: str,
                 timer_sec: int = 0,
                 using_usb: bool = True,
                 parent: typing.Optional['QObject'] = None
                 ) -> None:
        super().__init__(parent)

        # input parameters
        mode = 2					# sawtooth mode
        f0 = 5						# starting at 24.005 GHz
        BW = 240					# using all the BW available = 240 MHz
        Ns = 200					# 200 samples
        Ntar = 3					# 3 target of interest
        Rmax = 100					# searching along the full distance range
        MTI = 0		    			# MTI mode disable because we want information of static and moving targets
        Mth = 0			    		# parameter not used because "movement" is not requested
        Alpha = 10					# signal has to be 10 dB higher than its surrounding
        distance_true = True 		# request distance information
        velocity_true = False		# mode 2 does not provide velocity information
        SNR_true = True 			# Signal-to-Noise-Ratio information requested
        I_true = True 				# In-Phase Component (RAW data) not requested
        Q_true = True				# Quadrature Component (RAW data) not requested
        movement_true = False 		# not interested in boolean movement detection
        self.timeSleep = 5e-3       # Sleep Time (seconds) between iterations
        self.is_taking_data = True

        self.timer_sec = timer_sec

        # True if USB, False if UART
        self.usb_communication = using_usb

        self.ser = serial.Serial()
        
        if self.usb_communication:
            self.ser.baudrate = 1e6
        else:
            self.ser.baudrate = 115200

        self.ser.port = urad_port
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE

        try:
            self.ser.open()
        except Exception:
            self.close_radar()

        # switch ON uRAD
        return_code = uRAD_USB_SDK11.turnON(self.ser)
        if return_code != 0:
            return self.close_radar()

        if not self.usb_communication:
            time.sleep(self.timeSleep)

        # loadConfiguration uRAD
        return_code = uRAD_USB_SDK11.loadConfiguration(
            self.ser, mode, f0, BW,
            Ns, Ntar, Rmax, MTI, Mth, Alpha,
            distance_true, velocity_true, SNR_true,
            I_true, Q_true, movement_true
        )

        if return_code != 0:
            return self.close_radar()

        if not self.usb_communication:
            time.sleep(self.timeSleep)

        # Setup radar perhiperal
        send_raw_sec = lambda x: self.time.emit(x)

        if ultrasonic_port:
            self.ultrasonic = UltrasonicSensor(ultrasonic_port)

        self.timer = Timer(timer_sec)
        self.timer.time_lapsed_sec.connect(send_raw_sec)

    def close_radar(self) -> None:
        # switch OFF uRAD
        uRAD_USB_SDK11.turnOFF(self.ser)

        try:
            self.ser.close()
            self.ultrasonic.stop()
        except Exception:
            pass

        self.timer.stop()
        self.finished.emit()

    def run(self):
        phase_plot_data = np.linspace(0, 0, 100)[:-1]
        counter = 0

        self.timer.start()
        while self.is_taking_data:
            if self.timer_sec != 0 and self.timer.sec_remain < 0:
                break

            # target detection request
            return_code, results, raw_results = uRAD_USB_SDK11.detection(self.ser)
            if return_code != 0:
                return self.close_radar()

            # Extract results from outputs
            NtarDetected = results[0]
            distance = results[1]
            SNR = results[3]
            I = raw_results[0]
            Q = raw_results[1]
            
            # Iterate through desired targets
            for i in range(NtarDetected):
                # If SNR is not big enough
                if (SNR[i] < 0):
                    break

                data_i = np.array(I)
                data_q = np.array(Q)

                max_voltage = 3.3
                ADC_intervals = 4096
                Ns = np.size(data_i)
                Fs = 2

                data_i = np.subtract(np.multiply(I, max_voltage/ADC_intervals), np.mean(np.multiply(I, max_voltage/ADC_intervals)))
                data_q = np.subtract(np.multiply(Q, max_voltage/ADC_intervals), np.mean(np.multiply(Q, max_voltage/ADC_intervals)))
                ComplexVector = data_i + 1j*data_q
                ComplexVector = ComplexVector * np.hanning(Ns) * 2 / 3.3

                N_FFT = 4096
                FrequencyDomainComplex = 2 * np.absolute(np.fft.fft(ComplexVector))

                max_fft = max(FrequencyDomainComplex)
                index_fft = np.where(FrequencyDomainComplex == max_fft)[0][0]

                phase = np.angle(np.fft.fft(ComplexVector))
                size_fft = np.size(FrequencyDomainComplex)

                phase_plot_data[-1] = float(phase[index_fft])

                # Emit all the data to the GUI
                self.i_data.emit(data_i)
                self.q_data.emit(data_q)

                if counter % 10 == 0:
                    self.phase_plot.emit(phase_plot_data)
                    self.magnitude_plot.emit(FrequencyDomainComplex)

                self.magnitude_data.emit(FrequencyDomainComplex)
                self.peek_phase.emit(float(phase[index_fft]))

                try:
                    self.ultrasonic_data.emit(self.ultrasonic.read())
                except Exception:
                    pass

                phase_plot_data = np.append(phase_plot_data[1:], 0.0)

            #  time.sleep(0.3)
            counter += 1

            #  # If number of detected targets is greater than 0 prints an empty line for a smarter output
            if NtarDetected > 0:
                continue

            # Sleep during specified time
            if not self.usb_communication:
                time.sleep(self.timeSleep)

        return self.close_radar()
