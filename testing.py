from datetime import datetime
from typing import reveal_type

from matrix import Matrix
import fileutils
import math


class TestingSuiteError(BaseException):
    pass


def test_group(test_group_name, test_files, test_expected, test_function):
    test_amount = len(test_files)
    answer_file = open(test_expected, 'r', encoding='utf-8')
    test_answers = [eval(line.strip()) for line in answer_file.readlines()]
    print(f'Группа тестов: {test_group_name}')
    if len(test_answers) != test_amount:
        raise TestingSuiteError('Количество ответов не совпадает с количеством файлов')
    for i, filename in enumerate(test_files):
        start = datetime.now()
        actual = test_function(filename)
        expected = test_answers[i]
        end = datetime.now()
        print(f'Тест {i+1}: Результат = {actual}, Время = {end - start}')
        if type(actual) == float:
            assert abs(actual - expected) < 10 ** (math.log10(abs(expected) + 1e-9) - 12), \
                f'Тест {i+1}: {actual} != {expected}'
    print(f'{test_group_name}: тесты успешны')


if __name__ == '__main__':
    det_test_files = [f'tests/det/test_det{i:02}.txt' for i in range(1, 12 + 1)]
    test_group("Определитель матрицы", det_test_files, 'tests/det/test_det_expected.txt',
               lambda filename: Matrix(fileutils.read_matrix_from_file(filename)).det())
    print()
    print("Все тесты успешны")
