from matrix import Matrix
from fileutils import read_matrix_from_file


def test_invert(matrix):
    coef_column = Matrix([[x] for x in matrix.get_col(matrix.column_count - 1)])
    main_matrix = matrix.remove_col(matrix.column_count - 1)
    result = (main_matrix.get_inverse() * coef_column).get_col(0)
    return result


def test_is_eigen_correct(matrix):
    eig_vals, eig_vectors = matrix.get_eigenvectors_matrix()
    for i in range(len(eig_vals)):
        vector = Matrix([eig_vectors.get_col(i)]).transpose()
        eigen = eig_vals[i]
        if vector * eigen != matrix * vector:
            return False
    return True


TEST_FUNCS = [
    [
        lambda filename: Matrix(read_matrix_from_file(filename)).insert_row([69, 13, 37], 1),
        lambda filename: Matrix(read_matrix_from_file(filename)).insert_col([69, 13, 37], 1),
        lambda filename: Matrix(read_matrix_from_file(filename)).get_row(2),
        lambda filename: Matrix(read_matrix_from_file(filename)).get_col(3),
        lambda filename: Matrix(read_matrix_from_file(filename)).beautify_gauss(),
        lambda filename: Matrix(read_matrix_from_file(filename)).swap_rows(0, 1),
        lambda filename: Matrix(read_matrix_from_file(filename)).transpose(),
        lambda filename: Matrix(read_matrix_from_file(filename)).get_inverse(),
        lambda filename: (m := Matrix(read_matrix_from_file(filename))) * m.get_inverse()
    ],
    [
        lambda filename: Matrix(read_matrix_from_file(filename)).det()
    ] * 12,
    [
        lambda filename: Matrix(read_matrix_from_file(filename)).solve_cramer()
    ] * 11,
    [
        lambda filename: Matrix(read_matrix_from_file(filename)).solve_gauss()
    ] * 14,
    [
        lambda filename: test_invert(Matrix(read_matrix_from_file(filename)))
    ] * 11,
    [
        lambda filename: test_is_eigen_correct(Matrix(read_matrix_from_file(filename)))
    ] * 4
]