import sqlite3
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QLineEdit, QPushButton, QMainWindow, \
    QTableWidget, QGridLayout \
    , QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, QLabel, QMessageBox
import mysql.connector


class DataBaseConnection:
    def __init__(self, host="localhost" , user="root", password="pythoncourse", database="school"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database


    def connect(self):
        connection = mysql.connector.connect(host = self.host, user = self.user, password = self.password, database = self.database)
        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_student_action = QAction(QIcon("icons/add.png"), "Add student", self)
        add_student_action.triggered.connect(self.Insert)
        file_menu_item.addAction(add_student_action)
        search = QAction(QIcon("icons/search.png"), "Search", self)
        edit_menu_item.addAction(search)
        search.triggered.connect(self.search)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search)

        self.Status_bar = QStatusBar()
        self.setStatusBar(self.Status_bar)

        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusBar().removeWidget(child)

        self.Status_bar.addWidget(edit_button)
        self.Status_bar.addWidget(delete_button)

    def load_data(self):
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        result = cursor.fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def Insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """This app was created during the course "The Python Mega course"."""
        self.setText(content)


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete")
        yes = QPushButton("Yes")
        no = QPushButton("no")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1, )

        self.setLayout(layout)
        yes.clicked.connect(self.DeleteStudent)

    def DeleteStudent(self):
        index = mainwindow.table.currentRow()
        student_id = mainwindow.table.item(index, 0).text()

        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = %s", (student_id,))
        connection.commit()
        cursor.close()
        connection.close()
        mainwindow.load_data()
        self.close()

        confirmation = QMessageBox()
        confirmation.setWindowTitle("Success")
        confirmation.setText("The record was deleted successfully")
        confirmation.exec()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedHeight(300)
        self.setFixedWidth(300)

        layout = QVBoxLayout()

        index = mainwindow.table.currentRow()
        student_name = mainwindow.table.item(index, 1).text()

        self.student_id = mainwindow.table.item(index, 0).text()

        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        CourseName = mainwindow.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(CourseName)
        layout.addWidget(self.course_name)

        Mobile = mainwindow.table.item(index, 3).text()
        self.mobile_number = QLineEdit(Mobile)
        self.mobile_number.setPlaceholderText("Phone Number")
        layout.addWidget(self.mobile_number)

        submit = QPushButton("Update")
        layout.addWidget(submit)
        submit.clicked.connect(self.update_student)

        self.setLayout(layout)

    def update_student(self):
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = %s, course =%s, mobile = %s WHERE id = %s", (self.student_name.text(),
                                                                                            self.course_name.itemText(
                                                                                                self.course_name.currentIndex()),
                                                                                            self.mobile_number.text(),
                                                                                            self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        mainwindow.load_data()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedHeight(300)
        self.setFixedWidth(300)

        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        self.mobile_number = QLineEdit()
        self.mobile_number.setPlaceholderText("Phone Number")
        layout.addWidget(self.mobile_number)

        submit = QPushButton("Register")
        layout.addWidget(submit)
        submit.clicked.connect(self.add_students)

        self.setLayout(layout)

    def add_students(self):
        name = self.student_name.text()
        course = self.course_name.currentText()
        mobile = self.mobile_number.text()
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name,course, mobile) VALUES(%s, %s, %s)", (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        mainwindow.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student Data")
        self.setFixedHeight(300)
        self.setFixedWidth(300)

        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        self.setLayout(layout)

        submit = QPushButton("Search")
        layout.addWidget(submit)
        submit.clicked.connect(self.search)

    def search(self):
        name = self.student_name.text()
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE name = %s", (name,))
        result = cursor.fetchall()
        rows = list(result)
        print(rows)
        items = mainwindow.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            mainwindow.table.item(item.row(), 1).setSelected(True)
        cursor.close()
        connection.close()


app = QApplication(sys.argv)
mainwindow = MainWindow()
mainwindow.show()
mainwindow.load_data()
sys.exit(app.exec())
