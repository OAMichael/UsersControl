#!/usr/bin/python3

import os.path as op
import sqlite3
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel
from PyQt5.QtWidgets import QApplication, QTableWidgetItem
from PyQt5 import uic

def res_path(res_name):
    return op.join(op.dirname(__file__), res_name)

MainFormUI, MainForm = uic.loadUiType(res_path('Base.ui'))

class MainWindow(MainForm):
    def __init__(self, parent=None):
        # Initialize base form:
        super().__init__()
        # Create and initialize UI elements:
        self.ui = MainFormUI()
        self.ui.setupUi(self)
        self.con = QSqlDatabase.addDatabase("QSQLITE")
        self.con.setDatabaseName("worker_base.sqlite")
        if not self.con.open():
            print("Unable to connect to the database")
            sys.exit(1)

        self.setWindowTitle("Workers")
        
        query = QSqlQuery("SELECT * FROM users")
        while query.next():
            rows = self.ui.UsersTable.rowCount()
            self.ui.UsersTable.setRowCount(rows + 1)
            for i in range(4):
                self.ui.UsersTable.setItem(rows, i, QTableWidgetItem(str(query.value(i))))
        self.ui.UsersTable.resizeColumnsToContents()
        for i in range(4):
            self.ui.UsersTable.setSortingEnabled(True)

        query = QSqlQuery("SELECT * FROM computers")
        while query.next():
            rows = self.ui.ComputersTable.rowCount()
            self.ui.ComputersTable.setRowCount(rows + 1)
            for i in range(17):
                self.ui.ComputersTable.setItem(rows, i, QTableWidgetItem(str(query.value(i))))
        self.ui.ComputersTable.resizeColumnsToContents()
        for i in range(17):
            self.ui.ComputersTable.setSortingEnabled(True)

        query = QSqlQuery("SELECT * FROM applications")
        while query.next():
            rows = self.ui.ApplicationsTable.rowCount()
            self.ui.ApplicationsTable.setRowCount(rows + 1)
            for i in range(10):
                self.ui.ApplicationsTable.setItem(rows, i, QTableWidgetItem(str(query.value(i))))
        self.ui.ApplicationsTable.resizeColumnsToContents()
        for i in range(10):
            self.ui.ApplicationsTable.setSortingEnabled(True)


    def __del__(self):
        # Destroy reference to UI object:
        self.con.close()
        self.ui = None

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            try:
                self.con.close()
            except:
                pass
            sys.exit(1)
            

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
