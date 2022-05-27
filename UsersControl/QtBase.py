#!/usr/bin/python3

import os.path as op
import sqlite3
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel
from PyQt5.QtWidgets import QApplication, QTableWidgetItem
from PyQt5.QtGui import QPixmap
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
        self.row_users = 0
        self.row_computers = 0
        self.row_applications = 0

        self.ui.Refresh.clicked.connect(self.__update)
        self.con = QSqlDatabase.addDatabase("QSQLITE")
        self.con.setDatabaseName("worker_base.sqlite")
        if not self.con.open():
            print("Unable to connect to the database")
            sys.exit(1)

        self.setWindowTitle("Workers")
        
        self.__update()


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
        if key == Qt.Key_Space:
            self.__update()


    def __update(self):
        query = QSqlQuery(f"SELECT * FROM users WHERE Id > {self.row_users}")
        while query.next():
            rows = self.ui.UsersTable.rowCount()
            self.ui.UsersTable.setRowCount(rows + 1)
            for i in range(4):
                self.ui.UsersTable.setItem(rows, i, QTableWidgetItem(str(query.value(i))))
        self.ui.UsersTable.resizeColumnsToContents()
        for i in range(4):
            self.ui.UsersTable.setSortingEnabled(True)
        self.row_users = self.ui.UsersTable.rowCount()


        query = QSqlQuery(f"SELECT * from computers WHERE Id > {self.row_computers}")
        while query.next():
            rows = self.ui.ComputersTable.rowCount()
            self.ui.ComputersTable.setRowCount(rows + 1)
            for i in range(17):
                self.ui.ComputersTable.setItem(rows, i, QTableWidgetItem(str(query.value(i))))
        self.ui.ComputersTable.resizeColumnsToContents()
        for i in range(17):
            self.ui.ComputersTable.setSortingEnabled(True)
        self.row_computers = self.ui.ComputersTable.rowCount()


        query = QSqlQuery(f"SELECT * FROM applications WHERE Id > {self.row_applications}")
        while query.next():
            rows = self.ui.ApplicationsTable.rowCount()
            self.ui.ApplicationsTable.setRowCount(rows + 1)
            for i in range(10):
                self.ui.ApplicationsTable.setItem(rows, i, QTableWidgetItem(str(query.value(i))))
        self.ui.ApplicationsTable.resizeColumnsToContents()
        for i in range(10):
            self.ui.ApplicationsTable.setSortingEnabled(True)
        self.row_applications = self.ui.ApplicationsTable.rowCount()
            

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
