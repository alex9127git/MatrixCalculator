from mathutils import float_equals, multiply_row, add_rows, strf, is_zeroes


class Matrix:
    elements: list[list[float]]
    row_count: int
    column_count: int

    def __init__(self, elements):
        self.elements = elements
        self.row_count = len(elements)
        if self.row_count == 0:
            raise ValueError('Матрица не имеет ни одной строки')
        self.column_count = len(elements[0])
        if self.column_count == 0:
            raise ValueError('Матрица не имеет ни одного столбца')

    def __str__(self):
        result = ''
        for row in self.elements:
            result += '\t'.join(map(strf, row))
            result += '\n'
        return result.strip()

    def __eq__(self, other):
        if type(other) != Matrix:
            return False
        if self.row_count != other.row_count:
            return False
        if self.column_count != other.column_count:
            return False
        for r in range(self.row_count):
            for c in range(self.column_count):
                if not float_equals(self.elements[r][c], other.elements[r][c]):
                    return False
        return True

    def __ne__(self, other):
        return not (self == other)

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
        if size == 1:
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
        Приводит матрицу к виду, содержащему X строк и X + 1 столбцов, для решения методом Гаусса
        путём удаления столбцов, состоящих из нулей, и добавления строк с нулями.
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
        Сложность
        :return: Список корней системы линейных уравнений.
        """
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
                    solution.insert(0, row[-1] / row[r])
        return solution

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
        return Matrix([self.elements[i] for i in range(self.row_count) if i != r])

    def remove_col(self, c):
        """
        Удаляет столбец матрицы по индексу c.
        :param c: Индекс строки, которую нужно удалить.
        :return: Изменённая матрица.
        """
        return Matrix([self.elements[i][:c] + self.elements[i][c+1:] for i in range(self.row_count)])

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
