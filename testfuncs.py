from matrix import Matrix
from fileutils import read_matrix_from_file


TEST_FUNCS = [
    [
        lambda filename: Matrix(read_matrix_from_file(filename)).insert_row([69, 13, 37], 1),
        lambda filename: Matrix(read_matrix_from_file(filename)).insert_col([69, 13, 37], 1),
        lambda filename: Matrix(read_matrix_from_file(filename)).get_row(2),
        lambda filename: Matrix(read_matrix_from_file(filename)).get_col(3)
    ],
    [
        lambda filename: Matrix(read_matrix_from_file(filename)).det()
    ] * 12,
    [
        lambda filename: Matrix(read_matrix_from_file(filename)).solve_cramer()
    ] * 9
]