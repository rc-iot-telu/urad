from threading import Thread

import serial

class UltrasonicSensor:
    def __init__(self, port: str) -> None:
        self.device = serial.Serial(port, 9800, timeout=1)
        self.ultrasonic_data = 0

        t = Thread(target=self._update)
        t.daemon = True
        t.start()

    def _stop(self) -> None:
        self.stopped = True

    def read(self) -> float:
        return self.ultrasonic_data

    def _update(self) -> None:
        self.is_running = True

        while self.is_running:
            line = self.device.readline()

            if not line:
                continue

            data = line.decode().strip("\n")
            self.ultrasonic_data = float(data.strip("\n"))

    def stop(self) -> None:
        try:
            self.is_running = False
        except AttributeError:
            pass
