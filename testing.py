import os
from datetime import datetime

import mathutils
from mathutils import *
from testfuncs import *


TEST_FOLDER = 'tests'


class TestingSuiteError(BaseException):
    pass


def test(test_function, num, test_filename, expected=None):
    try:
        start = datetime.now()
        actual = test_function(test_filename)
        end = datetime.now()
        if type(actual) == float and expected is not None:
            print(f'Тест {num}: Результат = {actual}, Время = {end - start}')
            assert mathutils.float_equals(actual, expected), f'Тест {num}: {actual} != {expected}'
        else:
            print(f'Тест {num}:\nРезультат:\n{str(actual)}\nВремя = {end - start}')
            assert actual == expected, f'Тест {num}: {actual} != {expected}'
    except ValueError as e:
        assert str(e) == expected, f'Тест {num}: Тест не должен завершаться с ошибкой или должен выдавать другую ошибку'


def test_group(test_group_name, test_functions, test_filenames, answer_filename=None):
    """
    Проводит определённую группу тестов.
    :param test_group_name: Название группы тестов. Используется только для красивого вывода.
    :param test_functions: Список функций, которые требуется протестировать.
    :param test_filenames: Список вводных данных тестов.
    :param answer_filename: Список ожидаемых ответов.
    """
    test_amount = len(test_filenames)
    if answer_filename is not None:
        answer_file = open(answer_filename, 'r', encoding='utf-8')
        test_answers = [eval(line.strip()) for line in answer_file.readlines()]
    else:
        test_answers = [None] * test_amount
    print(f'Группа тестов: {test_group_name}')
    if len(test_answers) != test_amount:
        raise TestingSuiteError('Количество ответов не совпадает с количеством файлов')
    for i, f in enumerate(test_filenames):
        test(test_functions[i], i + 1, test_filenames[i], test_answers[i])
    print(f'{test_group_name}: тесты ' + ('успешны' if answer_filename is not None else 'выполнены'))
    print()


if __name__ == '__main__':
    folders = [os.path.join(TEST_FOLDER, f) for f in os.listdir(TEST_FOLDER)
               if os.path.isdir(os.path.join(TEST_FOLDER, f))]

    for test_group_id, curr_folder in enumerate(folders):
        exists_answers = os.path.exists(os.path.join(curr_folder, 'expected.txt'))
        test_count = len([os.path.join(curr_folder, f) for f in os.listdir(curr_folder)
                         if os.path.isfile(os.path.join(curr_folder, f))]) - (1 if exists_answers else 0)
        test_files = [os.path.join(curr_folder, f'{i:02}.txt') for i in range(1, test_count + 1)]
        test_group(curr_folder, TEST_FUNCS[test_group_id],
                   test_files, os.path.join(curr_folder, 'expected.txt') if exists_answers else None)
    print('Все тесты успешны')
