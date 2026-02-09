from datetime import datetime
from matrix import Matrix
import fileutils
import math


class TestingSuiteError(BaseException):
    pass


def determinator_tests():
    test_amount = 12
    test_files = [f'tests/det/test_det{i:02}.txt' for i in range(1, test_amount + 1)]
    test_answers = [-6, 130, 494698246, 26588, 4896412588, 0, 0, 1, 1307674368000, 137631185,
                    25583609102486527534082120267432973 / 20000000000000000000000000,
                    23018111199611624955679007896360261060337262458096508620829 / 250000000000000000000000000000]
    if len(test_answers) != test_amount:
        raise TestingSuiteError("Количество ответов не совпадает с количеством файлов")
    for i, filename in enumerate(test_files):
        start = datetime.now()
        matrix = Matrix(fileutils.read_matrix_from_file(filename))
        det = matrix.det()
        end = datetime.now()
        print(f"Тест {i+1}: Результат = {det}, Время = {end - start}")
        assert abs(det - test_answers[i]) < 10 ** (math.log10(abs(det) + 1e-9) - 10),\
            f"Тест {i+1}: {det} != {test_answers[i]}"

    print("Определитель матрицы: тесты успешны")


if __name__ == '__main__':
    determinator_tests()
    print()
    print("Все тесты успешны")
