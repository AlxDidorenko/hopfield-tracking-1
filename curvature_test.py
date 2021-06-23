import numpy as np
from _pytest.python_api import approx
from numpy.testing import assert_array_almost_equal, assert_array_equal, assert_array_almost_equal_nulp

from curvature import curvature_energy_pairwise, curvature_energy, curvature_energy_gradient, \
    curvature_energy_matrix, segment_find_next, segment_adjacent_pairs


def test_curvature_energy_pairwise():
    assert_array_equal(curvature_energy_pairwise(np.zeros((0, 3)), np.zeros((0, 3)), np.zeros((0, 3))),
                       np.zeros(0))

    a = np.array([[0., 0], [0., 1], [0., 2]])
    b = np.array([[1., 0], [1., 1], [1., 2]])
    c = np.array([[2., 0], [2, 0], [3, 4]])
    r2 = np.sqrt(2)
    assert_array_almost_equal(curvature_energy_pairwise(a, b, c),
                              [-0.5, -0.5 * (0.5 / r2) / r2, -0.5 * (0.5 / r2) / 2 / r2])
    assert_array_almost_equal(curvature_energy_pairwise(a, b, c, power=1),
                              [-0.5, -0.5 * (1 / r2) / r2, -0.5 * (1 / r2) / 2 / r2])
    assert_array_almost_equal(curvature_energy_pairwise(a, b, c, cosine_threshold=0.8),
                              [-0.5, 0, 0])


def test_segment_find_next():
    segments = np.array([[0, 1], [1, 3], [1, 4], [2, 3], [3, 4]])
    assert_array_equal(segment_find_next(segments, 0), np.array([[0, 1], [0, 2]]))
    assert_array_equal(segment_find_next(segments, 1), np.array([[1, 4]]))


def test_segment_adjacent_pairs():
    null_segment = np.empty((0, 2), dtype=int)
    assert_array_equal(segment_adjacent_pairs(null_segment), np.empty((0, 2), dtype=int))
    segments = np.array([[1, 3], [1, 4], [2, 3]])
    assert_array_equal(segment_adjacent_pairs(segments), np.empty((0, 2), dtype=int))
    segments = np.array([[1, 3], [1, 4], [2, 3], [3, 4]])
    assert_array_equal(np.sort(segment_adjacent_pairs(segments), axis=0),
                       [[0, 3], [2, 3]])
    segments = np.array([[7, 11], [7, 12], [0, 1], [1, 2], [1, 3], [1, 4], [2, 5], [3, 6]])
    assert_array_equal(np.sort(segment_adjacent_pairs(segments), axis=0),
                       [[2, 3], [2, 4], [2, 5], [3, 6], [4, 7]])


def test_curvature_energy_matrix():
    null_pos = np.empty((0, 2))
    null_segment = np.empty((0, 2), dtype=int)
    w = curvature_energy_matrix(null_pos, null_segment)
    assert w.shape == (0, 0)

    pos = np.array([[0., 0], [1., 0], [2., 0], [2, 1], [2, -1], [3, 0], [3, 2]])
    w = curvature_energy_matrix(pos, null_segment)
    assert w.shape == (0, 0)

    seg = np.array([[7, 11], [7, 12], [0, 1], [1, 2], [1, 3], [1, 4], [2, 5], [3, 6]])
    w = curvature_energy_matrix(pos, seg)
    s = -1 / 2  # straight cosine energy
    c = -1 / 8  # 45 degrees cosine energy
    l = - 1 / 4  # straight diagonal
    assert_array_almost_equal_nulp(w.A, [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, s, c, c, 0, 0],
        [0, 0, s, 0, 0, 0, s, 0],
        [0, 0, c, 0, 0, 0, 0, l],
        [0, 0, c, 0, 0, 0, 0, 0],
        [0, 0, 0, s, 0, 0, 0, 0],
        [0, 0, 0, 0, l, 0, 0, 0],
    ], 10)


def test_curvature_energy():
    pos = np.array([[0., 0], [1., 0], [2., 0], [2, 1], [2, -1], [3, 0], [3, 2]])
    seg = np.array([[0, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6]])
    w = curvature_energy_matrix(pos, seg)
    assert curvature_energy(w, np.array([1, 1, 0, 0, 0, 0])) == - 0.5
    assert curvature_energy(w, np.array([1, 0, 1, 0, 0, 0])) == approx(- 1. / 8)
    assert curvature_energy(w, np.array([1, 0, 0, 1, 0, 0])) == approx(- 1. / 8)
    assert curvature_energy(w, np.array([1, 0, 0, 0, 1, 0])) == approx(- 1. / 4)
    assert curvature_energy(w, np.array([1, 0, 0, 0, 0, 1])) == approx(- 1. / 16)
    assert curvature_energy(w, np.array([1, 1, 1, 1, 1, 1])) == approx(- 17. / 16)
    assert curvature_energy(w, np.array([1, .1, .1, .1, .1, .1])) == approx(- 1.7 / 16)


def test_curvature_energy_gradient():
    pos = np.array([[0., 0], [1., 0], [2., 0], [2, 1], [2, -1], [3, 0], [3, 2]])
    seg = np.array([[0, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6]])
    w = curvature_energy_matrix(pos, seg)
    act = np.array([1, 1, 0, 0, 0, 0])
    g = curvature_energy_gradient(w, act)
    assert_array_almost_equal(g, np.array([-0.5, -0.5, -1. / 8, -1. / 8, -1. / 4, -1. / 16]))