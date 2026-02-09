import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidget, QPushButton, QLabel, QTableWidgetItem, QFileDialog
from PyQt5 import uic

import fileutils
from matrix import Matrix


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class Window(QMainWindow):
    input_matrix_widget: QTableWidget
    calc_det_button: QPushButton
    read_matrix_button: QPushButton
    output_label: QLabel
    row_count: int
    column_count: int

    def __init__(self):
        super().__init__()
        uic.loadUi("form.ui", self)
        self.output_label.setText("Здесь появится результат вычислений")
        self.input_matrix_widget.setRowCount(1)
        self.input_matrix_widget.setColumnCount(1)
        self.row_count = 1
        self.column_count = 1
        self.input_matrix_widget.cellChanged.connect(self.update_table)
        self.calc_det_button.clicked.connect(self.calc_det)
        self.read_matrix_button.clicked.connect(self.read_file)

    def is_item_empty(self, r, c):
        return self.input_matrix_widget.item(r, c) is None or self.input_matrix_widget.item(r, c).text().strip() != ""

    def add_row(self):
        self.input_matrix_widget.setRowCount(self.row_count + 1)
        self.row_count += 1
        for c in range(self.column_count):
            self.input_matrix_widget.setItem(self.row_count - 1, c, QTableWidgetItem(""))

    def add_column(self):
        self.input_matrix_widget.setColumnCount(self.column_count + 1)
        self.column_count += 1
        for r in range(self.row_count):
            self.input_matrix_widget.setItem(r, self.column_count - 1, QTableWidgetItem(""))

    def remove_row(self):
        self.input_matrix_widget.setRowCount(self.row_count - 1)
        self.row_count -= 1

    def remove_column(self):
        self.input_matrix_widget.setColumnCount(self.column_count - 1)
        self.column_count -= 1

    def update_table(self):
        self.input_matrix_widget.blockSignals(True)
        for c in range(self.column_count):
            if self.is_item_empty(self.row_count - 1, c):
                self.add_row()
                break
        for r in range(self.row_count):
            if self.is_item_empty(r, self.column_count - 1):
                self.add_column()
                break
        can_delete_row = True
        for c in range(self.column_count):
            if self.is_item_empty(self.row_count - 2, c) or self.is_item_empty(self.row_count - 1, c):
                can_delete_row = False
        if can_delete_row:
            self.remove_row()
        can_delete_column = True
        for r in range(self.row_count):
            if self.is_item_empty(r, self.column_count - 2) or self.is_item_empty(r, self.column_count - 1):
                can_delete_column = False
        if can_delete_column:
            self.remove_column()
        self.input_matrix_widget.blockSignals(False)

    def calc_det(self):
        elements = []
        try:
            for r in range(self.row_count - 1):
                row = []
                for c in range(self.column_count - 1):
                    text = self.input_matrix_widget.item(r, c).text()
                    row.append(float(text) if text else 0)
                elements.append(row)
        except ValueError:
            self.output_label.setText("Элементы матрицы должны быть числами")
            return
        matrix = Matrix(elements)
        try:
            self.output_label.setText(f"Определитель матрицы = {str(matrix.det())}")
        except ValueError as e:
            self.output_label.setText(str(e))

    def read_file(self):
        filename = QFileDialog.getOpenFileName(self, "Выгрузка файла", ".")[0]
        self.input_matrix_widget.blockSignals(True)
        try:
            matrix = fileutils.read_matrix_from_file(filename)
            self.input_matrix_widget.setRowCount(0)
            self.input_matrix_widget.setColumnCount(0)
            self.input_matrix_widget.setRowCount(len(matrix) + 1)
            self.input_matrix_widget.setColumnCount(len(matrix[0]) + 1)
            self.row_count = len(matrix) + 1
            self.column_count = len(matrix[0]) + 1
            for r in range(len(matrix)):
                for c in range(len(matrix[0])):
                    self.input_matrix_widget.setItem(r, c, QTableWidgetItem(str(matrix[r][c])))
        except FileNotFoundError:
            self.output_label.setText("Не получилось прочитать файл")
        finally:
            self.input_matrix_widget.blockSignals(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())