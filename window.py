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
    active_table: int
    gauss_warning_displayed: bool

    def __init__(self):
        super().__init__()
        uic.loadUi('form.ui', self)
        self.status_widget.setText('Здесь появится результат вычислений')
        self.left_input_matrix_widget.setRowCount(1)
        self.left_input_matrix_widget.setColumnCount(1)
        self.right_input_matrix_widget.setRowCount(1)
        self.right_input_matrix_widget.setColumnCount(1)
        self.is_left_active = True
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

    def get_active_table(self):
        """
        Возвращает активную таблицу.
        :return: Левая таблица, если self.is_left_active = True, иначе правая таблица.
        """
        return self.left_input_matrix_widget if self.is_left_active else self.right_input_matrix_widget

    def toggle_input_matrix(self):
        """
        Переключает активную матрицу ввода.
        """
        self.is_left_active = not self.is_left_active
        active_id = 1 if self.is_left_active else 2
        other_id = 2 if self.is_left_active else 1
        self.current_input_label.setText(
            f'Следующие операции принимают Входную матрицу {active_id} в качестве входных данных')
        self.toggle_input_button.setText(f'Использовать Входную матрицу {other_id}')
        self.read_matrix_button.setText(f'Прочитать Входную матрицу {active_id} из файла')
        self.reuse_matrix_button.setText(f'Записать Выходную матрицу в Входную матрицу {active_id}')

    def swap_inputs(self):
        matrix1 = self.get_matrix_from_table(self.left_input_matrix_widget)
        matrix2 = self.get_matrix_from_table(self.right_input_matrix_widget)
        self.write_matrix_into_table(self.left_input_matrix_widget, matrix2)
        self.write_matrix_into_table(self.right_input_matrix_widget, matrix1)

    def copy_output_to_active(self):
        output = self.get_matrix_from_table(self.output_matrix_widget)
        self.write_matrix_into_table(self.get_active_table(), output)

    @staticmethod
    def is_item_empty(table, r, c):
        """
        Проверяет, что ячейка таблицы ввода с данными координатами не имеет содержимого.
        :param table: Таблица.
        :param r: Строка ячейки.
        :param c: Столбец ячейки.
        :return: True, если ячейка пустая; False, если ячейка непустая.
        """
        return table.item(r, c) is None or table.item(r, c).text().strip() != ""

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

    def update_table(self, table: QTableWidget):
        """
        Данный метод вызывается каждый раз, когда пользователь обновляет значение ячейки в таблице ввода.
        """
        table.blockSignals(True)
        for c in range(table.columnCount()):
            if self.is_item_empty(table, table.rowCount() - 1, c):
                self.add_row(table)
                break
        for r in range(table.rowCount()):
            if self.is_item_empty(table, r, table.columnCount() - 1):
                self.add_column(table)
                break
        can_delete_row = True
        for c in range(table.columnCount()):
            if (self.is_item_empty(table, table.rowCount() - 2, c) or
                    self.is_item_empty(table, table.rowCount() - 1, c)):
                can_delete_row = False
        if can_delete_row:
            self.remove_row(table)
        can_delete_column = True
        for r in range(table.rowCount()):
            if (self.is_item_empty(table, r, table.columnCount() - 2) or
                    self.is_item_empty(table, r, table.columnCount() - 1)):
                can_delete_column = False
        if can_delete_column:
            self.remove_column(table)
        table.blockSignals(False)

    def update_left_table(self):
        self.update_table(self.left_input_matrix_widget)

    def update_right_table(self):
        self.update_table(self.right_input_matrix_widget)

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
