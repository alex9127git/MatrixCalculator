import math
import numpy as np
import mathutils
from mathutils import float_equals, multiply_row, add_rows, strf, is_zeroes


class Matrix:
    elements: list[list[float]]
    row_count: int
    column_count: int

    def __init__(self, elements=None):
        if elements is None:
            self.row_count = 0
            self.column_count = 0
            self.elements = []
            return
        self.elements = elements
        self.row_count = len(elements)
        if self.row_count == 0:
            self.column_count = 0
            self.elements = []
            return
        self.column_count = len(elements[0])
        if self.column_count == 0:
            self.row_count = 0
            self.elements = []

    def __str__(self):
        result = ''
        for row in self.elements:
            result += '\t'.join(map(strf, row))
            result += '\n'
        return result.strip()

    def is_empty(self):
        return self.row_count == 0 or self.column_count == 0

    def has_nan(self):
        for row in self.elements:
            for elem in row:
                if math.isnan(elem):
                    return True
        return False

    def det(self):
        """
        Считает определитель квадратной матрицы рекурсивным способом с использованием кэширования.
        Сложность алгоритма = O(2^n), где n - размер матрицы.
        :return: Значение определителя.
        """
        return self.calc_det(dict(), self.row_count)[0]

    def calc_det(self, cache, size, bitmask=''):
        """
        Вспомогательная функция для расчёта определителя.
        :param cache: Вспомогательный параметр, хранящий расчёты рекурсивных вызовов этой функции.
        :param size: Размер матрицы. Можно обойтись без этого параметра, но с ним код выглядит лучше.
        :param bitmask: Вспомогательный параметр, используемый в качестве ключа для сохранения текущего рекурсивного
            вызова функции в словаре cache.
        :return: Кортеж, первым элементом которого является значение определителя,
            а вторым - кэш функции на данный момент.
        """
        if bitmask == '':
            bitmask = '0' * size
        if bitmask in cache:
            return cache[bitmask], cache
        if self.row_count != self.column_count:
            raise ValueError('Определитель матрицы не имеет смысл для матрицы, не являющейся квадратной')
        if self.has_nan():
            raise ValueError('Матрица имеет пустые ячейки')
        if self.is_empty():
            raise ValueError('Матрица пуста')
        elif size == 1:
            return self.elements[0][0], cache
        elif size == 2:
            value = self.elements[0][0] * self.elements[1][1] - self.elements[0][1] * self.elements[1][0]
            cache[bitmask] = value
            return value, cache
        else:
            d = 0
            for r in range(size):
                s = self.remove_row(r).remove_col(0)
                idx = [i for i, x in enumerate(bitmask) if x == '0'][r]
                b = bitmask[:idx] + '1' + bitmask[idx + 1:]
                m, cache = s.calc_det(cache, size - 1, b)
                d += ((-1) ** r) * self.elements[r][0] * m
            cache[bitmask] = d
            return d, cache

    def solve_cramer(self):
        """
        Считает корни системы линейных уравнений, представленной этой матрицей, методом Крамера.
        Сложность алгоритма = O(n*2^n), где n - количество строк матрицы.
        :return: Список корней системы линейных уравнений.
        """
        if self.is_empty():
            raise ValueError('Матрица пуста')
        if self.has_nan():
            raise ValueError('Матрица имеет пустые ячейки')
        if (self.row_count + 1) > self.column_count:
            raise ValueError(f'Слишком много уравнений для системы с {self.column_count - 1} неизвестными')
        if (self.row_count + 1) < self.column_count:
            raise ValueError(f'Слишком мало уравнений для системы с {self.column_count - 1} неизвестными')
        const_terms = self.get_col(self.column_count - 1)
        coefficients = self.remove_col(self.column_count - 1)
        denominator = coefficients.det()
        solution = []
        for c in range(coefficients.column_count):
            numerator = coefficients.replace_col(const_terms, c).det()
            if denominator == 0:
                if numerator == 0:
                    raise ValueError('Система имеет бесконечно много решений')
                else:
                    raise ValueError('Система не имеет решений')
            else:
                if numerator == 0:
                    solution.append(0.0)
                else:
                    solution.append(numerator / denominator)
        return solution

    def beautify_gauss(self):
        """
        Приводит матрицу к виду, содержащему максимум X строк и X + 1 столбцов, для решения методом Гаусса
        путём удаления столбцов, состоящих из нулей.
        :return: Изменённая матрица.
        """
        remaining_columns = []
        for c in range(self.column_count - 1):
            if not is_zeroes(self.get_col(c)):
                remaining_columns.append(c)
        remaining_columns.append(self.column_count - 1)
        remaining_elements = []
        for row in self.elements:
            remaining_elements.append([e for c, e in enumerate(row) if c in remaining_columns])
        return Matrix(remaining_elements)

    def convert_to_row_echelon(self):
        """
        Переводит матрицу линейных уравнений в ступенчатый вид, то есть такой,
        где для строки с индексом r первые r элементов являются нулями.
        :return: Матрица ступенчатого вида.
        """
        row_echelon = self.beautify_gauss()

        for sr in range(0, row_echelon.column_count - 2):
            if row_echelon.get_row(sr)[sr] == 0:
                r = sr
                while r < row_echelon.row_count and row_echelon.get_row(r)[sr] == 0:
                    r += 1
                if r == row_echelon.row_count:
                    if not is_zeroes(row_echelon.get_row(sr)):
                        row_echelon = row_echelon.insert_row([0] * row_echelon.column_count, sr)
                    continue
                else:
                    row_echelon = row_echelon.swap_rows(sr, r)
            head_row = row_echelon.get_row(sr)
            head_coef = head_row[sr]
            for r in range(sr + 1, row_echelon.row_count):
                curr_row = row_echelon.get_row(r)
                curr_coef = curr_row[sr]
                coef = -curr_coef / head_coef
                row_echelon = row_echelon.replace_row(add_rows(curr_row, multiply_row(head_row, coef)), r)
        return row_echelon

    def convert_to_diag(self):
        """
        Переводит матрицу линейных уравнений в диагональный вид, то есть такой,
        где для строки с индексом r все элементы, кроме элемента с индексом r, являются нулями.
        :return: Матрица диагонального вида.
        """
        row_echelon = self.convert_to_row_echelon()
        diag = Matrix(row_echelon.elements)
        for r in range(diag.row_count - 2, -1, -1):
            for c in range(r + 1, diag.row_count):
                head_row = diag.get_row(c)
                head_coef = head_row[c]
                if head_coef == 0:
                    continue
                curr_row = diag.get_row(r)
                curr_coef = curr_row[c]
                coef = -curr_coef / head_coef
                diag = diag.replace_row(add_rows(curr_row, multiply_row(head_row, coef)), r)
        return diag

    def solve_gauss(self):
        """
        Считает корни системы линейных уравнений, представленной этой матрицей, методом Гаусса.
        :return: Список корней системы линейных уравнений.
        """
        if self.is_empty():
            raise ValueError('Матрица пуста')
        if self.has_nan():
            raise ValueError('Матрица имеет пустые ячейки')
        diag = self.convert_to_diag()
        solution = []
        solution_undefined = False
        for r in range(diag.row_count - 1, -1, -1):
            row = diag.get_row(r)
            if row[r] == 0:
                if row[-1] != 0:
                    return []
                else:
                    solution.insert(0, 'любое')
                    solution_undefined = True
            else:
                if solution_undefined:
                    expr = strf(row[-1] / row[r])
                    for i in range(r + 1, len(row) - 1):
                        if row[i] == 0:
                            continue
                        coef = row[i] / row[r]
                        expr += f' {'+' if coef < 0 else '-'} {strf(abs(coef)) + ' ' if abs(coef) != 1 else ''}x{i+1}'
                    solution.insert(0, expr)
                else:
                    solution.insert(0, strf(row[-1] / row[r]))
        return solution

    def transpose(self):
        """
        Транспонирует матрицу, отражая её относительно главной диагонали так, что строки становятся столбцами,
        а столбцы - строками.
        :return: Транспонированная матрица.
        """
        submatrix = []
        for col in range(self.column_count):
            new_row = []
            for row in range(self.row_count):
                new_row.append(self.elements[row][col])
            submatrix.append(new_row)
        return Matrix(submatrix)


    def get_minor(self, row, col):
        """
        Вычисляет конкретный минор матрицы.
        :param row: Строка для удаления.
        :param col: Столбец для удаления.
        :return: Значение минора.
        """
        s = self.remove_row(row).remove_col(col)
        return s.det()

    def get_cofactor(self, row, col):
        """
        Вычисляет конкретное алгебраическое дополнение матрицы.
        :param row: Строка для удаления.
        :param col: Столбец для удаления.
        :return: Значение алгебраического дополнения.
        """
        return ((-1) ** (row + col + 2)) * self.get_minor(row, col)

    def get_adjugate(self):
        """
        Вычисляет присоединённую матрицу (матрицу, составленную из алгебраических дополнений своих элементов).
        :return: Присоединённая матрица.
        """
        result = []
        for row in range(self.row_count):
            new_row = []
            for col in range(self.column_count):
                new_row.append(self.get_cofactor(row, col))
            result.append(new_row)
        return Matrix(result)

    def get_inverse(self):
        if self.has_nan():
            raise ValueError('Матрица имеет пустые ячейки')
        if self.det() == 0:
            raise ValueError('Обратной матрицы не существует, определитель равен нулю')
        if self.row_count != self.column_count:
            raise ValueError('Обратной матрицы не существует, матрица не является квадратной')
        return self.get_adjugate().transpose() * (1 / self.det())

    def get_trace(self):
        if self.row_count != self.column_count:
            raise ValueError('След матрицы не имеет смысл для матрицы, не являющейся квадратной')
        if self.has_nan():
            raise ValueError('Матрица имеет пустые ячейки')
        if self.is_empty():
            raise ValueError('Матрица пуста')
        trace = 0
        for i in range(self.row_count):
            trace += self.elements[i][i]
        return trace

    def get_eigenvalues(self):
        """
        Высчитывает собственные значения матрицы.
        :return: Собственные значения матрицы, отсортированные в порядке возрастания.
        """
        if self.row_count != self.column_count:
            raise ValueError('Вычисление собственных значений не имеет смысла для матрицы, не являющейся квадратной')
        if self.has_nan():
            raise ValueError('Матрица имеет пустые ячейки')
        if self.is_empty():
            raise ValueError('Матрица пуста')
        size = self.row_count
        if size == 2:
            # λ² - λ * tr(A) + det(A) = 0
            t = self.get_trace()
            d = self.det()
            return sorted([(t - (t * t - 4 * d) ** 0.5) / 2, (t + (t * t - 4 * d) ** 0.5) / 2])
        else:
            return sorted(np.linalg.eig(self.elements).eigenvalues.tolist())

    def get_eigenvectors_matrix(self):
        eig = np.linalg.eig(np.array(self.elements, dtype=np.float64))
        eig_vals = eig.eigenvalues.tolist()
        eig_vectors = eig.eigenvectors.transpose().tolist()
        result = list(map(lambda x: x[1], sorted(zip(eig_vals, eig_vectors), key=lambda x: (x[0].real, x[0].imag))))
        return sorted(eig_vals, key=lambda x: (x.real, x.imag)), Matrix(result).transpose()

    def get_row(self, r) -> list[float]:
        """
        Возвращает строку матрицы по индексу r.
        :param r: Индекс строки, которую нужно получить.
        :return: Список с элементами строки r.
        """
        return self.elements[r]

    def get_col(self, c) -> list[float]:
        """
        Возвращает столбец матрицы по индексу c.
        :param c: Индекс столбца, который нужно получить.
        :return: Список с элементами столбца c.
        """
        return [row[c] for row in self.elements]

    def remove_row(self, r):
        """
        Удаляет строку матрицы по индексу r.
        :param r: Индекс строки, которую нужно удалить.
        :return: Изменённая матрица.
        """
        if self.row_count == 1 and r == 0:
            return Matrix()
        return Matrix([self.elements[i] for i in range(self.row_count) if i != r])

    def remove_col(self, c):
        """
        Удаляет столбец матрицы по индексу c.
        :param c: Индекс строки, которую нужно удалить.
        :return: Изменённая матрица.
        """
        if self.column_count == 1 and c == 0:
            return Matrix()
        return Matrix([self.elements[i][:c] + self.elements[i][c+1:] for i in range(self.row_count)])

    def append_row(self):
        """
        Добавляет строку в конец матрицы.
        :return: Изменённая матрица.
        """
        if self.is_empty():
            return Matrix([[math.nan]])
        return self.insert_row([math.nan] * self.column_count, self.row_count)

    def append_col(self):
        """
        Добавляет столбец в конец матрицы.
        :return: Изменённая матрица.
        """
        if self.is_empty():
            return Matrix([[math.nan]])
        return self.insert_col([math.nan] * self.row_count, self.column_count)

    def replace_val(self, row: int, col: int, value: float):
        """
        Заменяет значение по индексу строки и столбца на новое.
        :param row: Индекс строки.
        :param col: Индекс столбца.
        :param value: Новое значение.
        :return: Изменённая матрица.
        """
        submatrix = self.elements
        submatrix[row][col] = value
        return Matrix(submatrix)

    def insert_row(self, row: list[float], r: int):
        """
        Вставляет строку row в матрицу. Новая строка вставлена под индексом r.
        :param row: Строка для вставки.
        :param r: Индекс, куда будет вставлена строка.
        :return: Изменённая матрица.
        """
        submatrix = self.elements
        submatrix.insert(r, row)
        return Matrix(submatrix)

    def insert_col(self, col, c):
        """
        Вставляет столбец col в матрицу. Новый столбец вставлен под индексом c.
        :param col: Столбец для вставки.
        :param c: Индекс, куда будет вставлен столбец.
        :return: Изменённая матрица.
        """
        if self.is_empty():
            submatrix = [[] for _ in range(self.row_count)]
        else:
            submatrix = self.elements
        for i in range(self.row_count):
            submatrix[i].insert(c, col[i])
        return Matrix(submatrix)

    def replace_row(self, row, r):
        """
        Вставляет строку row в матрицу ВМЕСТО строки под индексом r.
        :param row: Строка для вставки.
        :param r: Индекс строки под замену.
        :return: Изменённая матрица.
        """
        return self.remove_row(r).insert_row(row, r)

    def replace_col(self, col, c):
        """
        Вставляет столбец col в матрицу ВМЕСТО столбца под индексом c.
        :param col: Столбец для вставки.
        :param c: Индекс столбца под замену.
        :return: Изменённая матрица.
        """
        return self.remove_col(c).insert_col(col, c)

    def swap_rows(self, r1, r2):
        """
        Меняет местами строки r1 и r2 в матрице.
        :param r1: Индекс первой строки.
        :param r2: Индекс второй строки.
        :return: Изменённая матрица.
        """
        row1 = self.get_row(r1)
        row2 = self.get_row(r2)
        return self.replace_row(row2, r1).replace_row(row1, r2)

    def __add__(self, other):
        if type(other) != Matrix:
            raise ValueError("Можно сложить только матрицу с матрицей")
        if self.row_count != other.row_count:
            raise ValueError("Количество строк складываемых матриц должно совпадать")
        if self.column_count != other.column_count:
            raise ValueError("Количество столбцов складываемых матриц должно совпадать")
        elements = []
        for r in range(self.row_count):
            new_row = []
            for c in range(self.column_count):
                new_row.append(self.elements[r][c] + other.elements[r][c])
            elements.append(new_row)
        return Matrix(elements)

    def __sub__(self, other):
        return self + (-other)

    def __eq__(self, other):
        if type(other) != Matrix:
            return False
        if self.row_count != other.row_count:
            return False
        if self.column_count != other.column_count:
            return False
        for r in range(self.row_count):
            for c in range(self.column_count):
                if not float_equals(self.elements[r][c], other.elements[r][c], precision=5):
                    return False
        return True

    def __ne__(self, other):
        return not (self == other)

    def __mul__(self, other):
        if type(other) == int or type(other) == float or type(other) == complex:
            elements = []
            for row in self.elements:
                new_row = []
                for elem in row:
                    new_row.append(elem * other)
                elements.append(new_row)
            return Matrix(elements)
        elif type(other) == Matrix:
            if self.column_count != other.row_count:
                raise ValueError(
                    'Количество столбцов первой матрицы должно совпадать с количеством строк второй матрицы')
            elements = []
            rows = [self.get_row(r) for r in range(self.row_count)]
            columns = [other.get_col(c) for c in range(other.column_count)]
            for row in range(self.row_count):
                new_row = []
                for col in range(other.column_count):
                    new_row.append(mathutils.scalar_multiply(rows[row], columns[col]))
                elements.append(new_row)
            return Matrix(elements)
        else:
            raise TypeError('Можно умножить матрицу только на число или на другую матрицу')

    def __neg__(self):
        return self * (-1)
