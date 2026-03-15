import os
from mathutils import float_equals, strf
from datetime import datetime
from testfuncs import *
TEST_FOLDER = 'tests'


class TestingSuiteError(BaseException):
    pass


def test(num, test_function, test_filename, expected=None):
    """
    Проводит один тест.
    :param num: Номер теста. Используется только для красивого вывода.
    :param test_function: Функция, которую необходимо протестировать.
    :param test_filename: Имя файла с входными данными для теста.
    :param expected: Ожидаемый результат. Если передаётся None, валидации теста не происходит.
    :return:
    """
    if test_group_id == 3 and num == 12:
        print('Entered debug')
    start = datetime.now()
    try:
        actual = test_function(test_filename)
        end = datetime.now()
        if expected is None:
            print(f'Тест {num}:\nРезультат:\n{str(actual)}\nВремя = {end - start}')
        elif type(actual) == float:
            print(f'Тест {num}: Результат = {actual}, Время = {end - start}')
            assert float_equals(actual, expected), f'Тест {num}: {actual} != {expected}'
        elif type(actual) == list and len(actual) > 0 and type(actual[0]) == float:
            print(f'Тест {num}: Результат = [{', '.join(map(strf, actual))}], Время = {end - start}')
            assert all([float_equals(actual[i], expected[i])
                        for i in range(max(len(actual), len(expected)))]), \
                f'Тест {num}: {actual} != {expected}'
        else:
            print(f'Тест {num}:\nРезультат:\n{str(actual)}\nВремя = {end - start}')
            assert actual == expected, f'Тест {num}: {actual} != {expected}'
    except ValueError as e:
        end = datetime.now()
        print(f'Тест {num}:\nРезультат:\n{str(e)}\nВремя = {end - start}')
        assert str(e) == expected, f'Тест {num}: Тест не должен завершаться с ошибкой или должен выдавать другую ошибку'


def test_group(test_group_name, test_functions, test_filenames, answer_filename=None):
    """
    Проводит определённую группу тестов.
    :param test_group_name: Название группы тестов. Используется только для красивого вывода.
    :param test_functions: Список функций, которые требуется протестировать.
    :param test_filenames: Список файлов с входными данными для тестов.
    :param answer_filename: Файл с ожидаемыми правильными ответами для тестов. Если передаётся None, предполагается,
    что правильные ответы для сравнения отсутствуют, и валидация тестов не происходит.
    """
    test_amount = len(test_filenames)
    if answer_filename is not None:
        answer_file = open(answer_filename, 'r', encoding='utf-8')
        test_answers = [eval(line.strip()) for line in answer_file.readlines()]
    else:
        test_answers = [None] * test_amount
    print(f'Группа тестов: {test_group_name}')
    if len(test_answers) != test_amount:
        raise TestingSuiteError('Количество ответов не совпадает с количеством файлов входных данных')
    if len(test_functions) != test_amount:
        raise TestingSuiteError('Количество тестов не совпадает с количеством файлов входных данных')
    for i, f in enumerate(test_filenames):
        test(i + 1, test_functions[i], test_filenames[i], test_answers[i])
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
