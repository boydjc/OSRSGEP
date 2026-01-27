import pandas as pd

from widgets import LineSep
from PySide6.QtCore import QAbstractTableModel, \
                           Qt
from PySide6.QtWidgets import QPushButton, \
                              QTableView, \
                              QHeaderView, \
                              QSizePolicy, \
                              QWidget, \
                              QVBoxLayout, \
                              QHBoxLayout, \
                              QLabel

class ScannerView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        layout.addWidget(ScannerViewControlBar(),0)

        self.scannerTable = QTableView()

        # make sure the table can expand to fill all remaining space
        self.scannerTable.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        testData = [
            {'item_id': 28924, 'item_name': 'Sunfire splinters', 'item_limit': 30000, 'low': 143, 'vol (5m)': 27047, 'high': 148, 'netSpreadPct': 0.0, 'lastTradeReadable': '15:08:01', 'lastTradeTime': 1769458081},
            {'item_id': 21880, 'item_name': 'Wrath rune', 'item_limit': 25000, 'low': 257, 'vol (5m)': 73110, 'high': 265, 'netSpreadPct': 0.0, 'lastTradeReadable': '15:07:53', 'lastTradeTime': 1769458073},
            {'item_id': 822, 'item_name': 'Mithril dart tip', 'item_limit': 20000, 'low': 107, 'vol (5m)': 13301, 'high': 114, 'netSpreadPct': 0.02, 'lastTradeReadable': '15:07:37', 'lastTradeTime': 1769458057},
            {'item_id': 823, 'item_name': 'Adamant dart tip', 'item_limit': 20000, 'low': 185, 'vol (5m)': 266270, 'high': 193, 'netSpreadPct': 0.01, 'lastTradeReadable': '15:07:40', 'lastTradeTime': 1769458060},
            {'item_id': 1395, 'item_name': 'Water battlestaff', 'item_limit': 18000, 'low': 8830, 'vol (5m)': 16506, 'high': 9043, 'netSpreadPct': 0.0, 'lastTradeReadable': '15:07:29', 'lastTradeTime': 1769458049},
            {'item_id': 1517, 'item_name': 'Maple logs', 'item_limit': 15000, 'low': 16, 'vol (5m)': 33606, 'high': 19, 'netSpreadPct': 0.04, 'lastTradeReadable': '15:08:17', 'lastTradeTime': 1769458097},
            {'item_id': 383, 'item_name': 'Raw shark', 'item_limit': 15000, 'low': 462, 'vol (5m)': 8262, 'high': 477, 'netSpreadPct': 0.01, 'lastTradeReadable': '15:08:18', 'lastTradeTime': 1769458098},
            {'item_id': 4822, 'item_name': 'Mithril nails', 'item_limit': 13000, 'low': 69, 'vol (5m)': 15422, 'high': 78, 'netSpreadPct': 0.07, 'lastTradeReadable': '15:08:09', 'lastTradeTime': 1769458089},
            {'item_id': 821, 'item_name': 'Steel dart tip', 'item_limit': 13000, 'low': 77, 'vol (5m)': 28318, 'high': 84, 'netSpreadPct': 0.04, 'lastTradeReadable': '15:08:07', 'lastTradeTime': 1769458087},
            {'item_id': 223, 'item_name': "Red spiders' eggs", 'item_limit': 13000, 'low': 156, 'vol (5m)': 11596, 'high': 164, 'netSpreadPct': 0.02, 'lastTradeReadable': '15:08:16', 'lastTradeTime': 1769458096}
        ]

        testDataFrame = pd.DataFrame(testData)
        

        self.tableModel = ScannerViewTableModel(testDataFrame)
        self.scannerTable.setModel(self.tableModel)
        # don't display row count
        self.scannerTable.verticalHeader().setVisible(False)
        # make sure the table columns stretch to fill the entire table
        self.scannerTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.scannerTable.setSortingEnabled(True)

        layout.addWidget(LineSep())

        layout.addWidget(self.scannerTable, 1)

        self.setLayout(layout)

class ScannerViewControlBar(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()

        self.lastScanTime = QLabel("Last Scan Time: 14:20")
        layout.addWidget(self.lastScanTime)

        layout.addStretch()

        self.scanPushButton = QPushButton(text="Scan", parent=self)
        layout.addWidget(self.scanPushButton)

        self.setLayout(layout)

    def setLastScanTime(self, text):
        self.lastScanTime.setText(text)


class ScannerViewTableModel(QAbstractTableModel):
    def __init__(self, df):
        super().__init__()
        self._data = df

    def setDataFrame(self, df):
        self.beginResetModel()
        self._data = df
        self.endResetModel()

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return "" if value is None else str(value)

    def rowCount(self, index=None):
        return self._data.shape[0]

    def columnCount(self, index=None):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])