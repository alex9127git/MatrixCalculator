class Matrix:
    elements: list[list[float]]
    row_count: int
    column_count: int

    def __init__(self, elements):
        self.elements = elements
        self.row_count = len(elements)
        self.column_count = len(elements[0])

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
            raise ValueError('Определитель матрицы не имеет смысл для неквадратной матрицы')
        if size == 1:
            return self.elements[0][0], cache
        elif size == 2:
            value = self.elements[0][0] * self.elements[1][1] - self.elements[0][1] * self.elements[1][0]
            cache[bitmask] = value
            return value, cache
        else:
            d = 0
            for r in range(size):
                s = self.get_submatrix(r, 0)
                idx = [i for i, x in enumerate(bitmask) if x == '0'][r]
                b = bitmask[:idx] + '1' + bitmask[idx + 1:]
                m, cache = s.calc_det(cache, size - 1, b)
                d += ((-1) ** r) * self.elements[r][0] * m
            cache[bitmask] = d
            return d, cache

    def get_submatrix(self, xr, xc):
        """
        Возвращает матрицу с удалённой строкой по индексу xr и удаленным столбцом по индексу xc.
        :param xr: Строка, которую нужно удалить. Передайте -1, чтобы не удалять строки.
        :param xc: Столбец, который нужно удалить. Передайте -1, чтобы не удалять столбцы.
        :return: Матрица с удалёнными строкой и столбцом, если это применимо.
        """
        submatrix = []
        for r in range(self.row_count):
            if r == xr:
                continue
            submatrix.append(self.elements[r] if xc == -1 else (self.elements[r][:xc] + self.elements[r][xc+1:]))
        return Matrix(submatrix)
