from app.utils.tsp_algorithm import solve_tsp_greedy


def test_empty_matrix():
    assert solve_tsp_greedy([]) == 0.0


def test_single_node():
    assert solve_tsp_greedy([[0.0]]) == 0.0


def test_two_nodes():
    matrix = [[0.0, 5.0], [5.0, 0.0]]
    assert solve_tsp_greedy(matrix) == 10.0


def test_three_nodes_simple():
    # 0 -> 1 -> 2 -> 0 : 1 + 1 + 2 = 4
    matrix = [
        [0.0, 1.0, 2.0],
        [1.0, 0.0, 1.0],
        [2.0, 1.0, 0.0],
    ]
    assert solve_tsp_greedy(matrix) == 4.0


def test_greedy_prefers_nearest_neighbor():
    # From node 0 the nearest neighbor is node 1 (1.0 vs 10.0)
    matrix = [
        [0.0, 1.0, 10.0],
        [1.0, 0.0, 1.0],
        [10.0, 1.0, 0.0],
    ]
    assert solve_tsp_greedy(matrix) == 12.0


def test_symmetric_round_trip_returns_to_start():
    matrix = [
        [0.0, 2.0, 3.0, 4.0],
        [2.0, 0.0, 5.0, 6.0],
        [3.0, 5.0, 0.0, 7.0],
        [4.0, 6.0, 7.0, 0.0],
    ]
    result = solve_tsp_greedy(matrix)
    # Route must start and end at node 0
    assert result == 2.0 + 5.0 + 7.0 + 4.0
