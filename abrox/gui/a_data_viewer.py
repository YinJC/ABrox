from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QAbstractTableModel
from a_dialogs import ALoadDataDialog
import tracksave


class ADataViewer(QFrame):
    """Represents a container for the table."""

    def __init__(self, model, console, parent=None):
        super(ADataViewer, self).__init__(parent)

        self._internalModel = model
        self._table = APandasView(console)
        self._toolbar = ATableToolbar(model, self._table, console)
        self._configureLayout(QVBoxLayout())

    def _configureLayout(self, layout):
        """Lays out the main components."""

        self.setFrameStyle(QFrame.Panel)
        layout.setSpacing(0)
        layout.addWidget(self._toolbar)
        layout.addWidget(self._table)
        self.setLayout(layout)


class APandasView(QTableView):
    """Represents the table view for the pandas data model."""
    def __init__(self, console, parent=None):
        super(APandasView, self).__init__(parent)

        self._console = console

    def updateTableAndModel(self, data, dataFileName):
        """A proxy method to update table."""

        # Create model
        model = APandasModel(data)

        # Add model to table
        self.setModel(model)

        # Push DataFrame to IPython
        self._console.addData(data, dataFileName)


class APandasModel(QAbstractTableModel):
    """
    Class to populate a Qt table view with a pandas data frame.
    Credit goes to: https://github.com/SanPen/GridCal/blob/master/UnderDevelopment/GridCal/gui/GuiFunctions.py
    """
    def __init__(self, data, parent=None, editable=False, editable_min_idx=-1):
        super(APandasModel, self).__init__(parent)
        self.data = data
        self._cols = data.columns
        self.index = data.index.values
        self.editable = editable
        self.editable_min_idx = editable_min_idx
        self.r, self.c = self.data.shape
        self.isDate = False
        self.formatter = lambda x: "%.2f" % x

    def flags(self, index):
        if self.editable and index.column() > self.editable_min_idx:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def rowCount(self, parent=None):
        return self.r

    def columnCount(self, parent=None):
        return self.c

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self.data.iloc[index.row(), index.column()])
        return None

    def setData(self, index, value, role=Qt.DisplayRole):

        try:
            self.data.iloc[index.row(), index.column()] = value
        except TypeError:
            QMessageBox.critical(self, 'Error...',
                                 'Trying to fill in data with a different format',
                                 QMessageBox.Ok)

    def headerData(self, p_int, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._cols[p_int]
            elif orientation == Qt.Vertical:
                if self.index is None:
                    return p_int
                else:
                    if self.isDate:
                        return self.index[p_int].strftime('%Y/%m/%d  %H:%M.%S')
                    else:
                        return str(self.index[p_int])
        return None

    def copy_to_column(self, row, col):
        """
        Copies one value to all the column
        @param row: Row of the value
        @param col: Column of the value
        @return: Nothing
        """
        self.data.iloc[:, col] = self.data.iloc[row, col]


class ATableToolbar(QFrame):
    """Represents a toolbar for the table."""

    def __init__(self, model, table, parent=None):
        super(ATableToolbar, self).__init__(parent)

        self._internalModel = model
        self._table = table
        self._label = QLabel('No Data File Loaded...  ')
        self._configureLayout(QHBoxLayout())

    def _configureLayout(self, layout):
        """Lays out the main toolbar components"""

        self.setFrameStyle(QFrame.WinPanel)
        # adjust layout
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # create load data button
        loadDataButton = QPushButton('Load Data')
        loadDataButton.setIcon(QIcon('icons/load.png'))
        loadDataButton.setFocusPolicy(Qt.NoFocus)
        loadDataButton.setToolTip('Load Data File...')
        loadDataButton.setStatusTip('Load Data File...')
        loadDataButton.clicked.connect(self._onLoad)

        layout.addWidget(loadDataButton)
        layout.addStretch(1)
        layout.addWidget(QLabel())
        layout.addWidget(self._label)
        self.setLayout(layout)

    def _onLoad(self):
        """Activated when button clicked."""

        loadedFileName = QFileDialog.getOpenFileName(self, 'Select a data file to load...',
                                                     "", "Data Files (*.csv *.txt *.dat)")
        # If something loaded, open properties dialog
        if loadedFileName[0]:
            dialog = ALoadDataDialog(loadedFileName[0], self)
            dialog.exec_()
            # If dialog accepted and loading ok
            if dialog.accepted:
                # Update internal model
                self._internalModel.addDataFile(loadedFileName[0])
                # Update table and table model
                self._table.updateTableAndModel(dialog.data, loadedFileName[0])
                # Update toolbar text
                self._label.setText('Showing: ' + loadedFileName[0] + '  ')
                # Update save flag
                tracksave.saved = False