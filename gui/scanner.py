import pandas as pd
import numpy as np
import traceback
from datetime import datetime

from PySide6.QtCore import (
    QAbstractTableModel, Qt, QObject, QThread, Signal, Slot, QSortFilterProxyModel
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
        self.scannerTable.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Source model
        self.tableModel = ScannerViewTableModel(pd.DataFrame())

        # Proxy for sorting (portable, correct numeric sorting)
        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.tableModel)
        self.proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self.proxy.setDynamicSortFilter(True)

        self.scannerTable.setModel(self.proxy)
        self.scannerTable.setSortingEnabled(True)

        self.scannerTable.verticalHeader().setVisible(False)
        self.scannerTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

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

        self.scanPushButton = QPushButton("Scan", self)
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

    def rowCount(self, parent=None):
        return 0 if self._data is None else self._data.shape[0]

    def columnCount(self, parent=None):
        return 0 if self._data is None else self._data.shape[1]

    def data(self, index, role):
        if not index.isValid() or self._data is None or self._data.empty:
            return None

        value = self._data.iat[index.row(), index.column()]

        # Raw values for sorting (UserRole exists in PySide6)
        if role == Qt.ItemDataRole.UserRole:
            if pd.isna(value):
                return None
            if isinstance(value, (np.generic,)):
                return value.item()
            return value

        # Pretty display
        if role == Qt.ItemDataRole.DisplayRole:
            if pd.isna(value):
                return ""
            return str(value)

        return None

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and self._data is not None and not self._data.empty:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
        return None


class ScannerController(QObject):
    resultsReady = Signal(object)  # pd.DataFrame
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

        self._thread = QThread(self)
        self._worker = ScanWorker(limit=10)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.result.connect(self._onResult)
        self._worker.error.connect(self.error)

        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(self._onFinished)

        self._thread.start()

    @Slot()
    def _onFinished(self):
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

    def __init__(self, limit=10):
        super().__init__()
        self._controller = GeController()
        self._limit = limit

    @Slot()
    def run(self):
        try:
            df = self._controller.findWidestSpreads(limit=self._limit)
            self.result.emit(df)
        except Exception:
            self.error.emit(traceback.format_exc())
        finally:
            self.finished.emit()