def read_matrix_from_file(filename):
    """
    Считывает двумерный массив дробных чисел из файла.
    :param filename: Имя файла для чтения.
    :return: Двумерный массив.
    """
    file = open(filename, 'r', encoding='utf-8')
    array = []
    for line in file.readlines():
        array.append(list(map(float, line.split())))
    return array


def write_matrix_into_file(array, filename):
    """
    Записывает двумерный массив дробных чисел в файл.
    :param array: Двумерный массив.
    :param filename: Имя файла для чтения.
    :return: Двумерный массив.
    """
    file = open(filename, 'w', encoding='utf-8')
    for row in array:
        file.write(' '.join(map(str, row)))
        file.write('\n')
