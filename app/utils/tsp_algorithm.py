def solve_tsp_greedy(matrix: list[list[float]]) -> float:
    if not matrix: return 0.0
    n = len(matrix)
    visited = [False] * n
    visited[0] = True
    current_node = 0
    total_dist = 0.0
    
    for _ in range(n - 1):
        next_node = -1
        min_dist = float('inf')
        for j in range(1, n):
            if not visited[j] and matrix[current_node][j] < min_dist:
                min_dist = matrix[current_node][j]
                next_node = j
        
        if next_node != -1:
            visited[next_node] = True
            total_dist += min_dist
            current_node = next_node
            
    total_dist += matrix[current_node][0]
    return total_dist