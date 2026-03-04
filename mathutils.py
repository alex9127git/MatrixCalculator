import math


def float_equals(n, m):
    """
    Сравнивает дробные числа с точностью до двенадцатого слева значащего знака.
    :param n: Первое число.
    :param m: Второе число.
    :return: Возвращает True, если числа равны, и False, если числа не равны.
    """
    return abs(n - m) < 10 ** (math.log10(abs(m) + 1e-9) - 12)