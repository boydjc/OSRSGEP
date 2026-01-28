import pandas as pd
import numpy as np

from PySide6.QtWidgets import (
                        QWidget,
                        QVBoxLayout,
                        QLabel,
                        QHBoxLayout,
                        QLineEdit,
                        QPushButton,
                        QTableView,
                        QSizePolicy,
                        QHeaderView
                    )

from PySide6.QtCore import (
    QAbstractTableModel, Qt, QObject, QThread, Signal, Slot, QSortFilterProxyModel
)

from .widgets import LineSep

class SearchView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        layout.addWidget(SearchControlBar())

        layout.addWidget(LineSep())

        layout.addWidget(SearchItemInfo())

        layout.addWidget(SearchTableContainer())
        
        self.setLayout(layout)

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

        self.itemTitle = QLabel("Manta Ray")
        self.itemSubtitle = QLabel("A rare catch")

        layout.addWidget(self.itemTitle, 0)
        layout.addWidget(self.itemSubtitle, 0)
        layout.addStretch()

        self.setLayout(layout)

    def setItemTitle(self, text):
        self.itemTitle = text

    def setItemSubtitle(self, text):
        self.itemSubtitle = text

class SearchItemDesc(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.itemMembers = QLabel("Members: True")
        self.itemLowAlch = QLabel("Low Alch: 60gp")
        self.itemHighAlch = QLabel("High Alch: 120gp")

        layout.addWidget(self.itemMembers, 0)
        layout.addWidget(self.itemLowAlch, 0)
        layout.addWidget(self.itemHighAlch, 0)
        layout.addStretch()

        self.setLayout(layout)

    def setItemMembers(self, text):
        self.itemMembers = text

    def setItemLowAlch(self, text):
        self.itemLowAlch = text

    def setItemHighAlch(self, text):
        self.itemHighAlch = text

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


