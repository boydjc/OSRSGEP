import pandas as pd
import numpy as np
import traceback
from typing import Optional

from PySide6.QtWidgets import (
                        QWidget,
                        QVBoxLayout,
                        QLabel,
                        QHBoxLayout,
                        QLineEdit,
                        QPushButton,
                        QTableView,
                        QSizePolicy,
                        QHeaderView,
                        QMessageBox,
                        
                    )

from PySide6.QtCore import (
    QAbstractTableModel, Qt, QObject, QThread, Signal, Slot, QSortFilterProxyModel
)

from PySide6.QtGui import QFont

from .widgets import LineSep
from controller import GeController

class SearchView(QWidget):
    def __init__(self):
        super().__init__()

        self.controller = SearchController()

        layout = QVBoxLayout()

        self.controlBar = SearchControlBar()
        layout.addWidget(self.controlBar)

        layout.addWidget(LineSep())

        self.itemInfo = SearchItemInfo()
        layout.addWidget(self.itemInfo)

        self.tables = SearchTableContainer()
        layout.addWidget(self.tables)

        self.setLayout(layout)

        # UI -> controller
        self.controlBar.itemSearchPushButton.clicked.connect(self._onSearchClicked)
        self.controlBar.itemIdSearchField.returnPressed.connect(self._onSearchClicked)

        # controller -> UI
        self.controller.latestReady.connect(self.tables.latestTableModel.setDataFrame)
        self.controller.fiveReady.connect(self.tables.fiveMinAveTableModel.setDataFrame)
        self.controller.infoReady.connect(self._applyInfo)
        self.controller.busyChanged.connect(self.controlBar.setBusy)
        self.controller.error.connect(self._onError)

    @Slot()
    def _onSearchClicked(self):
        txt = self.controlBar.itemIdSearchField.text().strip()
        try:
            item_id = int(txt)
            if item_id <= 0:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "Invalid item id", "Enter a positive integer item id.")
            return

        self.controller.search(item_id)

    @Slot(object)
    def _applyInfo(self, info: dict):
        # Defensive: missing keys OK
        name = info.get("name", "—")
        examine = info.get("examine", "—")
        members = info.get("members", False)
        lowalch = info.get("lowalch")
        highalch = info.get("highalch")

        self.itemInfo.searchItemTitle.setItemTitle(name)
        self.itemInfo.searchItemTitle.setItemSubtitle(examine)

        self.itemInfo.searchItemDesc.setItemMembers(members)
        self.itemInfo.searchItemDesc.setItemLowAlch(lowalch)
        self.itemInfo.searchItemDesc.setItemHighAlch(highalch)

    @Slot(str)
    def _onError(self, tb: str):
        # You can replace with QMessageBox.critical(...)
        print(tb)

class SearchControlBar(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Item Id: "))

        self.itemIdSearchField = QLineEdit()
        self.itemIdSearchField.setMaximumWidth(75)
        layout.addWidget(self.itemIdSearchField)

        layout.addStretch()

        self.itemSearchPushButton = QPushButton("Search", self)
        layout.addWidget(self.itemSearchPushButton)

        self.setLayout(layout)

    @Slot(bool)
    def setBusy(self, busy: bool):
        self.itemSearchPushButton.setEnabled(not busy)
        self.itemIdSearchField.setEnabled(not busy)
        self.itemSearchPushButton.setText("Searching..." if busy else "Search")

class SearchItemInfo(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()

        self.searchItemTitle = SearchItemTitle()
        self.searchItemDesc = SearchItemDesc()

        layout.addWidget(self.searchItemTitle)
        layout.addStretch()
        layout.addWidget(self.searchItemDesc)

        self.setLayout(layout)


class SearchItemTitle(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.itemTitle = QLabel("—")
        self.itemSubtitle = QLabel("—")

        # Make title larger and bold
        titleFont = QFont()
        titleFont.setPointSize(18)   # adjust as needed (16–22 typical)
        titleFont.setBold(True)
        self.itemTitle.setFont(titleFont)

        # Optional: slightly smaller subtitle
        subtitleFont = QFont()
        subtitleFont.setPointSize(11)
        self.itemSubtitle.setFont(subtitleFont)

        layout.addWidget(self.itemTitle, 0)
        layout.addWidget(self.itemSubtitle, 0)
        layout.addStretch()

        self.setLayout(layout)


class SearchItemDesc(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.itemMembers = QLabel("Members: —")
        self.itemLowAlch = QLabel("Low Alch: —")
        self.itemHighAlch = QLabel("High Alch: —")
        layout.addWidget(self.itemMembers, 0)
        layout.addWidget(self.itemLowAlch, 0)
        layout.addWidget(self.itemHighAlch, 0)
        layout.addStretch()
        self.setLayout(layout)

    def setItemMembers(self, is_members: bool):
        self.itemMembers.setText(f"Members: {bool(is_members)}")

    def setItemLowAlch(self, gp: Optional[int]):
        self.itemLowAlch.setText(f"Low Alch: {gp if gp is not None else '—'}gp")

    def setItemHighAlch(self, gp: Optional[int]):
        self.itemHighAlch.setText(f"High Alch: {gp if gp is not None else '—'}gp")

class SearchTableContainer(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.latestTable = QTableView()
        self.latestTable.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.latestTableModel = SearchViewTableModel(pd.DataFrame())
        self.latestTable.setModel(self.latestTableModel)
        self.latestTable.verticalHeader().setVisible(False)
        self.latestTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.fiveMinAveTable = QTableView()
        self.fiveMinAveTable.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.fiveMinAveTableModel = SearchViewTableModel(pd.DataFrame())
        self.fiveMinAveTable.setModel(self.fiveMinAveTableModel)
        self.fiveMinAveTable.verticalHeader().setVisible(False)
        self.fiveMinAveTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addWidget(QLabel("Latest"))
        layout.addWidget(self.latestTable)
        layout.addWidget(QLabel("5 Minute Average"))
        layout.addWidget(self.fiveMinAveTable)

        self.setLayout(layout)

class SearchViewTableModel(QAbstractTableModel):
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

        # Center all cell contents
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter

        # Raw values for sorting
        if role == Qt.ItemDataRole.UserRole:
            if pd.isna(value):
                return None
            if isinstance(value, (np.generic,)):
                return value.item()
            return value

        # Display text
        if role == Qt.ItemDataRole.DisplayRole:
            if pd.isna(value):
                return ""
            return str(value)

        return None
    
    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if self._data is not None and not self._data.empty:
                return str(self._data.columns[section])
        return None
    

class SearchWorker(QObject):
    finished = Signal()
    result = Signal(object, object, object)  # latest_df, five_df, info_dict
    error = Signal(str)

    def __init__(self, item_id: int):
        super().__init__()
        self._controller = GeController()
        self._item_id = item_id

    @Slot()
    def run(self):
        try:
            latest, five, info = self._controller.getLatest(self._item_id)

            latest_df = pd.DataFrame([latest]) if latest else pd.DataFrame()
            five_df   = pd.DataFrame([five]) if five else pd.DataFrame()

            self.result.emit(latest_df, five_df, info or {})
        except Exception:
            self.error.emit(traceback.format_exc())
        finally:
            self.finished.emit()


class SearchController(QObject):
    latestReady = Signal(object)      # pd.DataFrame
    fiveReady = Signal(object)        # pd.DataFrame
    infoReady = Signal(object)        # dict
    busyChanged = Signal(bool)
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self._busy = False
        self._thread = None
        self._worker = None

    def _setBusy(self, v: bool):
        if self._busy != v:
            self._busy = v
            self.busyChanged.emit(v)

    @Slot(int)
    def search(self, item_id: int):
        if self._busy:
            return

        self._setBusy(True)

        self._thread = QThread(self)
        self._worker = SearchWorker(item_id=item_id)
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

    @Slot(object, object, object)
    def _onResult(self, latest_df, five_df, info):
        self.latestReady.emit(latest_df)
        self.fiveReady.emit(five_df)
        self.infoReady.emit(info)


