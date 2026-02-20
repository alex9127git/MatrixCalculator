import os
from datetime import datetime

from matrix import Matrix
import fileutils
import math


TEST_FOLDER = 'tests'
TEST_GROUPS = ['Определитель матрицы']


class TestingSuiteError(BaseException):
    pass


def test_group(test_group_name, test_files, test_expected, test_function):
    """
    Проводит определённую группу тестов.
    :param test_group_name: Название группы тестов. Используется только для красивого вывода.
    :param test_files: Список вводных данных тестов.
    :param test_expected: Список ожидаемых ответов.
    :param test_function: Функция, которую требуется протестировать. Обязательно должна возвращать числовое значение.
    """
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
        else:
            raise TestingSuiteError('Тестовые функции, возвращающие нечисловые значения, не поддерживаются')
    print(f'{test_group_name}: тесты успешны')


if __name__ == '__main__':
    folders = [os.path.join(TEST_FOLDER, f) for f in os.listdir(TEST_FOLDER)
               if os.path.isdir(os.path.join(TEST_FOLDER, f))]
    for curr_folder in folders:
        test_count = len([os.path.join(curr_folder, f) for f in os.listdir(curr_folder)
                         if os.path.isfile(os.path.join(curr_folder, f))]) - 1
        test_files = [os.path.join(curr_folder, f'{i:02}.txt') for i in range(1, test_count + 1)]
        test_group('Определитель матрицы', test_files, os.path.join(curr_folder, 'expected.txt'),
                   lambda filename: Matrix(fileutils.read_matrix_from_file(filename)).det())
    print()
    print('Все тесты успешны')
