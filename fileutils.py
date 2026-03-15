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
