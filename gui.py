import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, \
                            QMainWindow, \
                            QWidget, \
                            QVBoxLayout, \
                            QHBoxLayout, \
                            QLabel, \
                            QComboBox            

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OSRSGEP")

        layout = QVBoxLayout()

        self.infoBar = InfoBar()

        layout.addWidget(self.infoBar)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


class InfoBar(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()

        self.gpLabel = QLabel("Total GP: 2,203,202")
        self.viewSelect = QComboBox()
        self.viewSelect.addItems(["Scanner", "Search"])

        layout.addWidget(self.gpLabel)
        layout.addStretch()
        layout.addWidget(self.viewSelect)

        self.setLayout(layout)

    def setGpLabel(self, text):
        self.gpLabel.setText(text)




if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec()
