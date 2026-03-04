from mathutils import float_equals


class Matrix:
    elements: list[list[float]]
    row_count: int
    column_count: int

    def __init__(self, elements):
        self.elements = elements
        self.row_count = len(elements)
        self.column_count = len(elements[0])

    def __str__(self):
        result = ''
        for row in self.elements:
            result += '\t'.join(map(str, row))
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
        if (self.row_count + 1) > self.column_count:
            raise ValueError(f'Слишком много уравнений для системы с {self.column_count - 1} неизвестными')
        if (self.row_count + 1) < self.column_count:
            raise ValueError(f'Слишком мало уравнений для системы с {self.column_count - 1} неизвестными')
        const_terms = self.get_col(self.column_count - 1)
        coefficients = self.remove_col(self.column_count - 1)
        denominator = coefficients.det()
        unknowns = []
        for c in range(coefficients.column_count):
            numerator = coefficients.replace_col(const_terms, c).det()
            if denominator == 0:
                if numerator == 0:
                    raise ValueError('Система имеет бесконечно много решений')
                else:
                    raise ValueError('Система не имеет решений')
            else:
                unknowns.append(numerator / denominator)
        return unknowns

    def get_row(self, r):
        """
        Возвращает строку матрицы по индексу r.
        :param r: Индекс строки, которую нужно получить.
        :return: Список с элементами строки r.
        """
        return self.elements[r]

    def get_col(self, c):
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

    def insert_row(self, row, r):
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

    def replace_col(self, col, c):
        """
        Вставляет столбец col в матрицу ВМЕСТО столбца под индексом c.
        :param col: Столбец для вставки.
        :param c: Индекс столбца под замену.
        :return: Изменённая матрица.
        """
        return self.remove_col(c).insert_col(col, c)
