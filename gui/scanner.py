import pandas as pd
import traceback
from datetime import datetime

from PySide6.QtCore import (
    QAbstractTableModel, Qt, QObject, QThread, Signal, Slot
)
from PySide6.QtWidgets import (
    QPushButton, QTableView, QHeaderView, QSizePolicy,
    QWidget, QVBoxLayout, QHBoxLayout, QLabel
)

from .widgets import LineSep
from controller import GeController


class ScannerView(QWidget):
    def __init__(self):
        super().__init__()

        self.scannerController = ScannerController()

        layout = QVBoxLayout()

        self.controlBar = ScannerViewControlBar()
        layout.addWidget(self.controlBar, 0)

        self.scannerTable = QTableView()
        self.scannerTable.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        self.tableModel = ScannerViewTableModel(pd.DataFrame())
        self.scannerTable.setModel(self.tableModel)

        self.scannerTable.verticalHeader().setVisible(False)
        self.scannerTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.scannerTable.setSortingEnabled(True)

        layout.addWidget(LineSep())
        layout.addWidget(self.scannerTable, 1)
        self.setLayout(layout)

        # Wiring
        self.controlBar.scanPushButton.clicked.connect(self.scannerController.scan)
        self.scannerController.resultsReady.connect(self.tableModel.setDataFrame)
        self.scannerController.lastScanTimeChanged.connect(
            lambda t: self.controlBar.setLastScanTime(f"Last Scan Time: {t}")
        )
        self.scannerController.busyChanged.connect(self.controlBar.setBusy)
        self.scannerController.error.connect(self._onError)

    @Slot(str)
    def _onError(self, tb: str):
        print(tb)


class ScannerViewControlBar(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()

        self.lastScanTime = QLabel("Last Scan Time: --:--:--")
        layout.addWidget(self.lastScanTime)

        layout.addStretch()

        self.scanPushButton = QPushButton(text="Scan", parent=self)
        layout.addWidget(self.scanPushButton)

        self.setLayout(layout)

    def setLastScanTime(self, text: str):
        self.lastScanTime.setText(text)

    @Slot(bool)
    def setBusy(self, busy: bool):
        self.scanPushButton.setEnabled(not busy)
        self.scanPushButton.setText("Scanning..." if busy else "Scan")

class ScannerViewTableModel(QAbstractTableModel):
    def __init__(self, df: pd.DataFrame):
        super().__init__()
        self._data = df

    @Slot(object)
    def setDataFrame(self, df: pd.DataFrame):
        self.beginResetModel()
        self._data = df if df is not None else pd.DataFrame()
        self.endResetModel()

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return "" if value is None else str(value)
        return None

    def rowCount(self, parent=None):
        return 0 if self._data is None else self._data.shape[0]

    def columnCount(self, parent=None):
        return 0 if self._data is None else self._data.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and self._data is not None:
            if orientation == Qt.Orientation.Horizontal and section < len(self._data.columns):
                return str(self._data.columns[section])
            if orientation == Qt.Orientation.Vertical and section < len(self._data.index):
                return str(self._data.index[section])
        return None


class ScannerController(QObject):
    resultsReady = Signal(object)     # pd.DataFrame
    error = Signal(str)
    busyChanged = Signal(bool)
    lastScanTimeChanged = Signal(str)

    def __init__(self):
        super().__init__()
        self._busy = False
        self._thread = None
        self._worker = None

    def _setBusy(self, v: bool):
        if self._busy != v:
            self._busy = v
            self.busyChanged.emit(v)

    @Slot()
    def scan(self):
        if self._busy:
            return
        self._setBusy(True)

        self._thread = QThread()
        self._worker = ScanWorker()
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.result.connect(self._onResult)
        self._worker.error.connect(self.error)

        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(self._onThreadFinished)

        self._thread.start()

    @Slot()
    def _onThreadFinished(self):
        self._worker = None
        self._thread = None
        self._setBusy(False)

    @Slot(object)
    def _onResult(self, df: pd.DataFrame):
        self.resultsReady.emit(df)
        self.lastScanTimeChanged.emit(datetime.now().strftime("%H:%M:%S"))


class ScanWorker(QObject):
    finished = Signal()
    result = Signal(object)   # pd.DataFrame
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self._controller = GeController()

    @Slot()
    def run(self):
        try:
            df = self._controller.findWidestSpreads()
            self.result.emit(df)
        except Exception:
            self.error.emit(traceback.format_exc())
        finally:
            self.finished.emit()