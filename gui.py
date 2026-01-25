import sys
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OSRSGEP")

        widget = Color("red")
        self.setCentralWidget(widget)

# test widget
class Color(QWidget):
    def __init__(self, color):
        super().__init__()
        # tell widget to automatically fill the background with color
        self.setAutoFillBackground(True)

        # getting the current palette (the global desktop palette by default)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)




if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec()
