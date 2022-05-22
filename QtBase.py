#!/usr/bin/python3

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QTableWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QTableWidgetItem, QTableView, QComboBox, QStackedLayout
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel
import sys


class Users(QWidget):
    def __init__(self):
        super(Users, self).__init__()
        
        # Set up the view and load the data
        self.view = QTableWidget()
        self.view.setColumnCount(4)
        self.view.setHorizontalHeaderLabels(["ID", "Name", "Computer", "IP"])
        query = QSqlQuery("SELECT * FROM users")
        while query.next():
            rows = self.view.rowCount()
            self.view.setRowCount(rows + 1)
            for i in range(4):
                self.view.setItem(rows, i, QTableWidgetItem(str(query.value(i))))

        self.view.resizeColumnsToContents()


class Computers(QWidget):
    def __init__(self):
        super(Computers, self).__init__()
        
        # Set up the view and load the data
        self.view = QTableWidget()
        self.view.setColumnCount(17)
        self.view.setHorizontalHeaderLabels(["ID", "Computer", "Mostly used window", "Second mostly used window",
                                             "Third mostly used window", "Mostly used window percent", 
                                             "Second mostly used window percent", "Third mostly used window percent",
                                             "Currently active window", "Number of opened windows", "Disk memory usage", 
                                             "Min CPU frequency", "Max CPU frequency", "Current CPU frequency",
                                             "System boot time", "Total memory used", "Timestamp"])
        query = QSqlQuery("SELECT * FROM computers")
        while query.next():
            rows = self.view.rowCount()
            self.view.setRowCount(rows + 1)
            for i in range(17):
                new_info = str(query.value(i))
                if (i > 4 and i < 8) or i == 10 or i == 15:
                    new_info += "%"
                elif i > 10 and i < 14:
                    new_info += " MHz"
                self.view.setItem(rows, i, QTableWidgetItem(new_info))

        self.view.resizeColumnsToContents()


class Applications(QWidget):
    def __init__(self):
        super(Applications, self).__init__()
        
        # Set up the view and load the data
        self.view = QTableWidget()
        self.view.setColumnCount(10)
        self.view.setHorizontalHeaderLabels(["ID", "Application name", "Computer", "Create time", "Status", 
                                             "RSS memory", "VMS memory", "Shared memory", "Data memory", "Timestamp"])
        query = QSqlQuery("SELECT * FROM applications")
        while query.next():
            rows = self.view.rowCount()
            self.view.setRowCount(rows + 1)
            for i in range(10):
                self.view.setItem(rows, i, QTableWidgetItem(str(query.value(i))))

        self.view.resizeColumnsToContents()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(1600, 900)
        
        pagelayout = QVBoxLayout()
        button_layout = QHBoxLayout()
        self.stacklayout = QStackedLayout()

        pagelayout.addLayout(button_layout)
        pagelayout.addLayout(self.stacklayout)

        button = QComboBox()
        button.addItems(["Users", "Computers", "Applications"])

        # Sends the current index (position) of the selected item.
        button.currentIndexChanged.connect(self.turn_table)
        button_layout.addWidget(button)

        self.users_table = Users()
        self.stacklayout.addWidget(self.users_table.view)

        self.computers_table = Computers()
        self.stacklayout.addWidget(self.computers_table.view)

        self.applications_table = Applications()
        self.stacklayout.addWidget(self.applications_table.view)

        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)

    def turn_table(self, i):
        self.stacklayout.setCurrentIndex(i)


def main():
    app = QApplication(sys.argv)
    global con
    con = QSqlDatabase.addDatabase("QSQLITE")
    con.setDatabaseName("worker_base.sqlite")
    if not con.open():
        print("Unable to connect to the database")
        sys.exit(1)

    base = MainWindow()
    base.setWindowTitle("Workers")
    base.show()   
    app.exit()
    sys.exit(app.exec_())
    con.close()


if __name__ == "__main__":
	main()