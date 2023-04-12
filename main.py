import sys
import os

import qdarktheme

from PyQt5.QtWidgets import QApplication

from urad import MainWindow


def main():
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication([])

    ex = MainWindow()
    ex.setMinimumSize(1280, 720)
    ex.show()

    app.setStyleSheet(qdarktheme.load_stylesheet("light"))

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
