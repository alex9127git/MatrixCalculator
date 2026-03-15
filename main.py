import sys
from typing import Any

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import *
from PyQt5 import uic

import fileutils
from matrix import Matrix


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class Window(QMainWindow):
    input_matrix_widget: QTableWidget
    calc_det_button: QPushButton
    solve_cramer_button: QPushButton
    solve_gauss_button: QPushButton
    read_matrix_button: QPushButton
    status_widget: QTextEdit
    row_count: int
    column_count: int
    gauss_warning_displayed: bool

    def __init__(self):
        super().__init__()
        uic.loadUi('form.ui', self)
        self.status_widget.setText('Здесь появится результат вычислений')
        self.input_matrix_widget.setRowCount(1)
        self.input_matrix_widget.setColumnCount(1)
        self.row_count = 1
        self.column_count = 1
        self.input_matrix_widget.cellChanged.connect(self.update_table)
        self.calc_det_button.clicked.connect(self.calc_det)
        self.solve_cramer_button.clicked.connect(self.solve_cramer)
        self.solve_gauss_button.clicked.connect(self.solve_gauss)
        self.read_matrix_button.clicked.connect(self.read_file)
        self.gauss_warning_displayed = False

    def is_item_empty(self, r, c):
        """
        Проверяет, что ячейка таблицы ввода с данными координатами не имеет содержимого.
        :param r: Строка ячейки.
        :param c: Столбец ячейки.
        :return: True, если ячейка пустая; False, если ячейка непустая.
        """
        return self.input_matrix_widget.item(r, c) is None or self.input_matrix_widget.item(r, c).text().strip() != ""

    def add_row(self):
        """
        Добавляет строку в таблицу ввода.
        """
        self.input_matrix_widget.setRowCount(self.row_count + 1)
        self.row_count += 1
        for c in range(self.column_count):
            self.input_matrix_widget.setItem(self.row_count - 1, c, QTableWidgetItem(""))

    def add_column(self):
        """
        Добавляет столбец в таблицу ввода.
        """
        self.input_matrix_widget.setColumnCount(self.column_count + 1)
        self.column_count += 1
        for r in range(self.row_count):
            self.input_matrix_widget.setItem(r, self.column_count - 1, QTableWidgetItem(""))

    def remove_row(self):
        """
        Удаляет строку из таблицы ввода.
        """
        self.input_matrix_widget.setRowCount(self.row_count - 1)
        self.row_count -= 1

    def remove_column(self):
        """
        Удаляет столбец из таблицы ввода.
        """
        self.input_matrix_widget.setColumnCount(self.column_count - 1)
        self.column_count -= 1

    def update_table(self):
        """
        Данный метод вызывается каждый раз, когда пользователь обновляет значение ячейки в таблице ввода.
        """
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
        """
        Считывает матрицу из таблицы ввода и производит расчёт определителя.
        """
        self.status_widget.setText('Выполняется...')
        self.status_widget.repaint()
        elements = self.get_matrix_from_table()
        if elements is None:
            return
        try:
            matrix = Matrix(elements)
            result = matrix.det()
            self.status_widget.setText(f'Определитель матрицы = {result:g}')
        except ValueError as e:
            self.status_widget.setText(str(e))

    def solve_cramer(self):
        """
        Считывает матрицу из таблицы ввода и решает систему линейных уравнений из матрицы методом Крамера.
        """
        self.status_widget.setText('Выполняется...')
        self.status_widget.repaint()
        elements = self.get_matrix_from_table()
        if elements is None:
            return
        try:
            matrix = Matrix(elements)
            result = matrix.solve_cramer()
            status_string = 'Система имеет решение:\n'
            for i, x in enumerate(result):
                if i != 0:
                    status_string += ', '
                status_string += f'x{i+1} = {result[i]}'
            self.status_widget.setText(status_string)
        except ValueError as e:
            self.status_widget.setText(str(e))

    def solve_gauss(self):
        """
        Считывает матрицу из таблицы ввода и решает систему линейных уравнений из матрицы методом Гаусса.
        """
        self.status_widget.setText('Выполняется...')
        self.status_widget.repaint()
        elements = self.get_matrix_from_table()
        if elements is None:
            return
        try:
            matrix = Matrix(elements)
            if matrix.beautify_gauss() != matrix and not self.gauss_warning_displayed:
                self.gauss_warning_displayed = True
                status_string = ('Матрица имеет неиспользуемые неизвестные и будет преобразована.\n'
                                 'Нажмите на кнопку ещё раз, чтобы продолжить.')
                self.status_widget.setTextColor(QColor(255, 0, 0))
            else:
                self.gauss_warning_displayed = False
                self.write_matrix_into_table(matrix.beautify_gauss().elements)
                result = matrix.solve_gauss()
                if len(result) == 0:
                    status_string = 'Система не имеет решений'
                else:
                    status_string = 'Система имеет решение:\n'
                    for i, x in enumerate(result):
                        if i != 0:
                            status_string += ', '
                        status_string += f'x{i+1} = {result[i]}'
                        self.status_widget.setTextColor(QColor(0, 0, 0))
            self.status_widget.setText(status_string)
        except ValueError as e:
            self.status_widget.setText(str(e))

    def read_file(self):
        """
        Считывает матрицу из файла и записывает её в таблицу ввода.
        """
        filename = QFileDialog.getOpenFileName(self, 'Выгрузка файла', '.')[0]
        try:
            matrix = fileutils.read_matrix_from_file(filename)
            self.write_matrix_into_table(matrix)
        except FileNotFoundError:
            self.status_widget.setText('Не получилось прочитать файл')

    def write_matrix_into_table(self, matrix: list[Any]):
        self.input_matrix_widget.blockSignals(True)
        self.input_matrix_widget.setRowCount(0)
        self.input_matrix_widget.setColumnCount(0)
        self.input_matrix_widget.setRowCount(len(matrix) + 1)
        self.input_matrix_widget.setColumnCount(len(matrix[0]) + 1)
        self.row_count = len(matrix) + 1
        self.column_count = len(matrix[0]) + 1
        for r in range(len(matrix)):
            for c in range(len(matrix[0])):
                self.input_matrix_widget.setItem(r, c, QTableWidgetItem(str(matrix[r][c])))
        self.input_matrix_widget.blockSignals(False)

    def get_matrix_from_table(self):
        """
        Считывает список элементов из исходной таблицы.
        :return: Список элементов
        """
        elements = []
        try:
            for r in range(self.row_count - 1):
                row = []
                for c in range(self.column_count - 1):
                    text = self.input_matrix_widget.item(r, c).text()
                    row.append(float(text) if text else 0)
                elements.append(row)
        except ValueError:
            self.status_widget.setText('Элементы матрицы должны быть числами')
            return None
        return elements


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())