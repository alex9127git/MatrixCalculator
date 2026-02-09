import math
from datetime import datetime

import fileutils


class Matrix:
    def __init__(self, elements):
        self.elements = elements
        self.row_count = len(elements)
        self.column_count = len(elements[0])

    def det(self):
        return self.calc_det(dict(), self.row_count)[0]

    def calc_det(self, cache, size, bitmask=""):
        if bitmask == "":
            bitmask = '0' * size
        if bitmask in cache:
            return cache[bitmask], cache
        if self.row_count != self.column_count:
            raise ValueError("Определитель матрицы не имеет смысл для неквадратной матрицы")
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
        submatrix = []
        for r in range(self.row_count):
            if r == xr:
                continue
            submatrix.append(self.elements[r][:xc] + self.elements[r][xc+1:])
        return Matrix(submatrix)
