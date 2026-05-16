from typing import Any
from PyQt5 import uic
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QTableWidget, QPushButton, QTextEdit, QTableWidgetItem, QFileDialog, QLabel
import fileutils
from mathutils import strf
from matrix import Matrix


class Window(QMainWindow):
    left_input_matrix_widget: QTableWidget
    right_input_matrix_widget: QTableWidget
    output_matrix_widget: QTableWidget
    calc_det_button: QPushButton
    calc_eigen_button: QPushButton
    calc_invert_button: QPushButton
    calc_product_button: QPushButton
    solve_cramer_button: QPushButton
    solve_gauss_button: QPushButton
    solve_invert_button: QPushButton
    read_matrix_button: QPushButton
    reuse_matrix_button: QPushButton
    write_matrix_button: QPushButton
    toggle_input_button: QPushButton
    switch_inputs_button: QPushButton
    current_input_label: QLabel
    status_widget: QTextEdit
    active_id: int
    gauss_warning_displayed: bool
    data: list[Matrix]

    def __init__(self):
        super().__init__()
        uic.loadUi('form.ui', self)
        self.status_widget.setText('Здесь появится результат вычислений')
        self.left_input_matrix_widget.setRowCount(1)
        self.left_input_matrix_widget.setColumnCount(1)
        self.right_input_matrix_widget.setRowCount(1)
        self.right_input_matrix_widget.setColumnCount(1)
        self.active_id = 0
        self.left_input_matrix_widget.cellChanged.connect(self.update_left_table)
        self.right_input_matrix_widget.cellChanged.connect(self.update_right_table)
        self.calc_det_button.clicked.connect(self.calc_det)
        self.calc_invert_button.clicked.connect(self.calc_invert)
        self.calc_product_button.clicked.connect(self.calc_product)
        self.solve_cramer_button.clicked.connect(self.solve_cramer)
        self.solve_gauss_button.clicked.connect(self.solve_gauss)
        self.solve_invert_button.clicked.connect(self.solve_invert)
        self.read_matrix_button.clicked.connect(self.read_file)
        self.toggle_input_button.clicked.connect(self.toggle_input_matrix)
        self.reuse_matrix_button.clicked.connect(self.copy_output_to_active)
        self.switch_inputs_button.clicked.connect(self.swap_inputs)
        self.gauss_warning_displayed = False
        self.data = [Matrix(), Matrix(), Matrix()]

    def get_active_table(self):
        """
        :return: Активная таблица.
        """
        return self.left_input_matrix_widget if self.active_id == 0 else self.right_input_matrix_widget

    def toggle_input_matrix(self):
        """
        Переключает активную матрицу ввода.
        """
        self.active_id = (self.active_id + 1) % 2
        other_id = (self.active_id + 1) % 2
        self.current_input_label.setText(
            f'Следующие операции принимают Входную матрицу {self.active_id + 1} в качестве входных данных')
        self.toggle_input_button.setText(f'Использовать Входную матрицу {other_id + 1}')
        self.read_matrix_button.setText(f'Прочитать Входную матрицу {self.active_id + 1} из файла')
        self.reuse_matrix_button.setText(f'Записать Выходную матрицу в Входную матрицу {self.active_id + 1}')

    def swap_inputs(self):
        matrix1 = self.get_matrix_from_table(self.left_input_matrix_widget)
        matrix2 = self.get_matrix_from_table(self.right_input_matrix_widget)
        self.write_matrix_into_table(self.left_input_matrix_widget, matrix2)
        self.write_matrix_into_table(self.right_input_matrix_widget, matrix1)

    def copy_output_to_active(self):
        output = self.get_matrix_from_table(self.output_matrix_widget)
        self.write_matrix_into_table(self.get_active_table(), output)

    @staticmethod
    def item_exists(table, r, c):
        """
        Проверяет, что ячейка таблицы ввода с данными координатами имеет содержимое.
        :param table: Таблица.
        :param r: Строка ячейки.
        :param c: Столбец ячейки.
        :return: True, если ячейка непустая; False, если ячейка пустая.
        """
        return table.item(r, c).text().strip() != ""

    @staticmethod
    def add_row(table: QTableWidget):
        """
        Добавляет строку в таблицу ввода.
        :param table: Таблица.
        """
        table.setRowCount(table.rowCount() + 1)
        for c in range(table.columnCount()):
            table.setItem(table.rowCount() - 1, c, QTableWidgetItem(""))

    @staticmethod
    def add_column(table: QTableWidget):
        """
        Добавляет столбец в таблицу ввода.
        :param table: Таблица.
        """
        table.setColumnCount(table.columnCount() + 1)
        for r in range(table.rowCount()):
            table.setItem(r, table.columnCount() - 1, QTableWidgetItem(""))

    @staticmethod
    def remove_row(table: QTableWidget):
        """
        Удаляет строку из таблицы ввода.
        :param table: Таблица.
        """
        table.setRowCount(table.rowCount() - 1)

    @staticmethod
    def remove_column(table: QTableWidget):
        """
        Удаляет столбец из таблицы ввода.
        :param table: Таблица.
        """
        table.setColumnCount(table.columnCount() - 1)

    def update_table(self, t_id: int, row: int, col: int):
        """
        Данный метод вызывается каждый раз, когда пользователь обновляет значение ячейки в таблице ввода.
        """
        table = [self.left_input_matrix_widget, self.right_input_matrix_widget, self.output_matrix_widget][t_id]
        table.blockSignals(True)
        value = float(table.item(row, col).text()) if self.item_exists(table, row, col) else 0
        matrix = self.data[t_id]
        if row >= matrix.row_count:
            matrix = matrix.append_row()
        if col >= matrix.column_count:
            matrix = matrix.append_col()
        matrix = matrix.replace_val(row, col, value)
        for c in range(table.columnCount()):
            if self.item_exists(table, table.rowCount() - 1, c):
                self.add_row(table)
                break
        for r in range(table.rowCount()):
            if self.item_exists(table, r, table.columnCount() - 1):
                self.add_column(table)
                break
        can_delete_row = True
        while can_delete_row and table.rowCount() > 1:
            for c in range(table.columnCount()):
                if (self.item_exists(table, table.rowCount() - 2, c) or
                        self.item_exists(table, table.rowCount() - 1, c)):
                    can_delete_row = False
            if can_delete_row:
                self.remove_row(table)
                matrix = matrix.remove_row(matrix.row_count - 1)
        can_delete_column = True
        while can_delete_column and table.columnCount() > 1:
            for r in range(table.rowCount()):
                if (self.item_exists(table, r, table.columnCount() - 2) or
                        self.item_exists(table, r, table.columnCount() - 1)):
                    can_delete_column = False
            if can_delete_column:
                self.remove_column(table)
                matrix = matrix.remove_col(matrix.column_count - 1)
        self.data[t_id] = matrix
        print(self.data[t_id])
        table.blockSignals(False)

    def update_left_table(self, row, col):
        self.update_table(0, row, col)

    def update_right_table(self, row, col):
        self.update_table(1, row, col)

    def calc_det(self):
        """
        Считывает матрицу из таблицы ввода и производит расчёт определителя.
        """
        self.status_widget.setText('Выполняется...')
        self.status_widget.repaint()
        elements = self.get_matrix_from_table(self.get_active_table())
        if elements is None:
            self.status_widget.setText('Входная матрица пустая')
            return
        try:
            matrix = Matrix(elements)
            result = matrix.det()
            self.status_widget.setText(f'Определитель матрицы = {strf(result)}')
        except ValueError as e:
            self.status_widget.setText(str(e))

    def calc_invert(self):
        self.status_widget.setText('Выполняется...')
        self.status_widget.repaint()
        elements = self.get_matrix_from_table(self.get_active_table())
        if elements is None:
            self.status_widget.setText('Входная матрица пустая')
            return
        try:
            matrix = Matrix(elements)
            inverted_matrix = matrix.get_inverse()
            self.write_matrix_into_table(self.output_matrix_widget, inverted_matrix.elements)
            self.status_widget.setText('Обратная матрица выведена на экран')
        except ValueError as e:
            self.status_widget.setText(str(e))

    def calc_product(self):
        self.status_widget.setText('Выполняется...')
        self.status_widget.repaint()
        elements1 = self.get_matrix_from_table(self.left_input_matrix_widget)
        elements2 = self.get_matrix_from_table(self.right_input_matrix_widget)
        if elements1 is None or elements2 is None:
            self.status_widget.setText('Одна из входных матриц пустая')
            return
        try:
            matrix1 = Matrix(elements1)
            matrix2 = Matrix(elements2)
            product = matrix1 * matrix2
            self.write_matrix_into_table(self.output_matrix_widget, product.elements)
            self.status_widget.setText('Произведение матриц выведено на экран')
        except ValueError as e:
            self.status_widget.setText(str(e))

    def solve_cramer(self):
        """
        Считывает матрицу из таблицы ввода и решает систему линейных уравнений из матрицы методом Крамера.
        """
        self.status_widget.setText('Выполняется...')
        self.status_widget.repaint()
        elements = self.get_matrix_from_table(self.get_active_table())
        if elements is None:
            self.status_widget.setText('Входная матрица пустая')
            return
        try:
            matrix = Matrix(elements)
            result = matrix.solve_cramer()
            status_string = 'Система имеет решение:\n'
            for i, x in enumerate(result):
                if i != 0:
                    status_string += ', '
                status_string += f'x{i+1} = {strf(result[i])}'
            self.status_widget.setText(status_string)
        except ValueError as e:
            self.status_widget.setText(str(e))

    def solve_gauss(self):
        """
        Считывает матрицу из таблицы ввода и решает систему линейных уравнений из матрицы методом Гаусса.
        """
        self.status_widget.setText('Выполняется...')
        self.status_widget.repaint()
        elements = self.get_matrix_from_table(self.get_active_table())
        if elements is None:
            self.status_widget.setText('Входная матрица пустая')
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
                self.write_matrix_into_table(self.get_active_table(), matrix.beautify_gauss().elements)
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

    def solve_invert(self):
        self.status_widget.setText('Выполняется...')
        self.status_widget.repaint()
        elements = self.get_matrix_from_table(self.get_active_table())
        if elements is None:
            self.status_widget.setText('Входная матрица пустая')
            return
        try:
            matrix = Matrix(elements)
            coef_column = Matrix([[x] for x in matrix.get_col(matrix.column_count - 1)])
            main_matrix = matrix.remove_col(matrix.column_count - 1)
            result = (main_matrix.get_inverse() * coef_column).get_col(0)
            status_string = 'Система имеет решение:\n'
            for i, x in enumerate(result):
                if i != 0:
                    status_string += ', '
                status_string += f'x{i + 1} = {strf(result[i])}'
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
            self.write_matrix_into_table(self.get_active_table(), matrix)
        except FileNotFoundError:
            self.status_widget.setText('Не получилось прочитать файл')

    @staticmethod
    def write_matrix_into_table(table: QTableWidget, matrix: list[Any]):
        table.blockSignals(True)
        table.setRowCount(0)
        table.setColumnCount(0)
        table.setRowCount(len(matrix) + 1)
        table.setColumnCount(1 if len(matrix) == 0 else len(matrix[0]) + 1)
        for r in range(len(matrix)):
            for c in range(len(matrix[0])):
                table.setItem(r, c, QTableWidgetItem(str(matrix[r][c])))
        table.blockSignals(False)

    def get_matrix_from_table(self, table):
        """
        Считывает список элементов из исходной таблицы.
        :return: Список элементов.
        """
        elements = []
        try:
            for r in range(table.rowCount() - 1):
                row = []
                for c in range(table.columnCount() - 1):
                    text = table.item(r, c).text()
                    row.append(float(text) if text else 0)
                elements.append(row)
        except ValueError:
            self.status_widget.setText('Элементы матрицы должны быть числами')
            return None
        return elements
