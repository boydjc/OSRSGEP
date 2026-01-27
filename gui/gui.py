import sys

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication, \
                            QMainWindow, \
                            QWidget, \
                            QVBoxLayout, \
                            QHBoxLayout, \
                            QLabel, \
                            QComboBox, \
                            QStackedLayout

from scanner import ScannerView
from widgets import LineSep

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OSRSGEP")
        self.setMinimumSize(1200, 800)

        layout = QVBoxLayout()

        self.infoBar = InfoBar()
        self.stackedDisplay = StackedDisplay()
        self.infoBar.viewChanged.connect(self.stackedDisplay.switchDisplay)

        layout.addWidget(self.infoBar, 0)
        layout.addWidget(LineSep())
        layout.addWidget(self.stackedDisplay, 1)
        layout.addStretch()

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
class InfoBar(QWidget):
    viewChanged = Signal(str)

    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()

        self.gpLabel = QLabel("Total GP: 2,203,202")
        self.viewSelect = QComboBox()
        self.viewSelect.addItems(["Scanner", "Search"])
        self.viewSelect.currentTextChanged.connect(self.viewChanged.emit)

        layout.addWidget(self.gpLabel)
        layout.addStretch()
        layout.addWidget(self.viewSelect)

        self.setLayout(layout)

    def setGpLabel(self, text):
        self.gpLabel.setText(text)

# this is for showing everything basically under the info bar    
class StackedDisplay(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.stackedLayout = QStackedLayout()

        layout.addLayout(self.stackedLayout)

        self.scannerView = ScannerView()
        self.searchView = SearchView()

        self.stackedLayout.addWidget(self.scannerView)
        self.stackedLayout.addWidget(self.searchView)

        self.setLayout(layout)

    def switchDisplay(self, viewStr):
        if viewStr == "Scanner":
            self.stackedLayout.setCurrentIndex(0)
        elif viewStr == "Search":
            self.stackedLayout.setCurrentIndex(1)
        

class SearchView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Search View"))
        
        self.setLayout(layout)


if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec()
