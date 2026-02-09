def read_matrix_from_file(filename):
    file = open(filename, 'r', encoding='utf-8')
    array = []
    for line in file.readlines():
        array.append(list(map(float, line.split())))
    return array
