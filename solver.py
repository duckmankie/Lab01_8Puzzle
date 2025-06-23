from collections import deque
import copy
import time
import heapq

def serialize(board):
    return tuple(val for row in board for val in row)

GOAL_STATE = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def manhattan_distance(board):
    distance = 0
    for r in range(3):
        for c in range(3):
            val = board[r][c]
            if val == 8:
                continue
            goal_r, goal_c = val // 3, val % 3
            distance += abs(r - goal_r) + abs(c - goal_c)
    return distance

def bfs(start_board):
    start = copy.deepcopy(start_board)
    queue = deque([(start, [])])
    visited = set()
    visited.add(serialize(start))
    nodes_expanded = 0
    start_time = time.perf_counter()
    while queue:
        board, path = queue.popleft()
        nodes_expanded += 1
        if board == GOAL_STATE:
            end_time = time.perf_counter()
            solve_time = end_time - start_time
            total_cost = len(path)
            frontier_nodes = len(queue)
            return path, nodes_expanded, total_cost, solve_time, frontier_nodes
        br, bc = find_blank(board)
        for dr, dc in MOVES:
            nr, nc = br + dr, bc + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                new_board = copy.deepcopy(board)
                new_board[br][bc], new_board[nr][nc] = new_board[nr][nc], new_board[br][bc]
                key = serialize(new_board)
                if key not in visited:
                    visited.add(key)
                    queue.append((new_board, path + [(nr, nc)]))
    end_time = time.perf_counter()
    solve_time = end_time - start_time
    frontier_nodes = len(queue)
    return [], nodes_expanded, 0, solve_time, frontier_nodes

def dfs(start_board, max_depth=500):
    start = copy.deepcopy(start_board)
    visited = set()
    path = []
    nodes_expanded = 0
    start_time = time.perf_counter()
    def recursive_dfs(board, depth):
        nonlocal nodes_expanded
        if board == GOAL_STATE:
            return True
        if depth >= max_depth:
            return False
        key = serialize(board)
        visited.add(key)
        nodes_expanded += 1
        br, bc = find_blank(board)
        for dr, dc in MOVES:
            nr, nc = br + dr, bc + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                new_board = copy.deepcopy(board)
                new_board[br][bc], new_board[nr][nc] = new_board[nr][nc], new_board[br][bc]
                new_key = serialize(new_board)
                if new_key not in visited:
                    path.append((nr, nc))
                    if recursive_dfs(new_board, depth + 1):
                        return True
                    path.pop()
        return False
    found = recursive_dfs(start, 0)
    end_time = time.perf_counter()
    solve_time = end_time - start_time
    total_cost = len(path) if found else 0
    frontier_nodes = 1 if not found else 0
    return (path if found else []), nodes_expanded, total_cost, solve_time, frontier_nodes

def iddfs(start_board, max_depth=500):
    start = copy.deepcopy(start_board)
    nodes_expanded = 0
    start_time = time.perf_counter()
    def dls(board, depth_limit, path, visited):
        nonlocal nodes_expanded
        if board == GOAL_STATE:
            return path
        if len(path) >= depth_limit:
            return None
        key = serialize(board)
        visited.add(key)
        nodes_expanded += 1
        br, bc = find_blank(board)
        for dr, dc in MOVES:
            nr, nc = br + dr, bc + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                new_board = copy.deepcopy(board)
                new_board[br][bc], new_board[nr][nc] = new_board[nr][nc], new_board[br][bc]
                new_key = serialize(new_board)
                if new_key not in visited:
                    path.append((nr, nc))
                    result = dls(new_board, depth_limit, path, visited)
                    if result is not None:
                        return result
                    path.pop()
        return None
    for depth in range(1, max_depth + 1):
        visited = set()
        path = []
        result = dls(start, depth, path, visited)
        if result is not None:
            end_time = time.perf_counter()
            solve_time = end_time - start_time
            total_cost = len(result)
            frontier_nodes = 1
            return result, nodes_expanded, total_cost, solve_time, frontier_nodes
    end_time = time.perf_counter()
    solve_time = end_time - start_time
    frontier_nodes = 1
    return [], nodes_expanded, 0, solve_time, frontier_nodes

def find_blank(board):
    for r in range(3):
        for c in range(3):
            if board[r][c] == 8:
                return r, c
    return None, None

def ucs(start_board):
    start = copy.deepcopy(start_board)
    visited = set()
    heap = []
    nodes_expanded = 0
    start_time = time.perf_counter()
    heapq.heappush(heap, (0, start, []))
    while heap:
        cost, board, path = heapq.heappop(heap)
        key = serialize(board)
        if key in visited:
            continue
        visited.add(key)
        nodes_expanded += 1
        if board == GOAL_STATE:
            end_time = time.perf_counter()
            solve_time = end_time - start_time
            total_cost = cost
            frontier_nodes = len(heap)
            return path, nodes_expanded, total_cost, solve_time, frontier_nodes
        br, bc = find_blank(board)
        for dr, dc in MOVES:
            nr, nc = br + dr, bc + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                new_board = copy.deepcopy(board)
                new_board[br][bc], new_board[nr][nc] = new_board[nr][nc], new_board[br][bc]
                new_key = serialize(new_board)
                if new_key not in visited:
                    heapq.heappush(heap, (cost + 1, new_board, path + [(nr, nc)]))
    end_time = time.perf_counter()
    solve_time = end_time - start_time
    frontier_nodes = len(heap)
    return [], nodes_expanded, 0, solve_time, frontier_nodes

def ida_star(start_board):
    start_time = time.perf_counter()
    bound = manhattan_distance(start_board)
    path = []
    nodes_expanded = 0
    def dfs(board, g, bound, path, visited):
        nonlocal nodes_expanded
        f = g + manhattan_distance(board)
        if f > bound:
            return f
        if board == GOAL_STATE:
            return True
        visited.add(serialize(board))
        nodes_expanded += 1
        min_bound = float('inf')
        br, bc = find_blank(board)
        for dr, dc in MOVES:
            nr, nc = br + dr, bc + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                new_board = copy.deepcopy(board)
                new_board[br][bc], new_board[nr][nc] = new_board[nr][nc], new_board[br][bc]
                new_key = serialize(new_board)
                if new_key not in visited:
                    path.append((nr, nc))
                    t = dfs(new_board, g + 1, bound, path, visited)
                    if t is True:
                        return True
                    if isinstance(t, (int, float)):
                        min_bound = min(min_bound, t)
                    path.pop()
        return min_bound
    while True:
        visited = set()
        t = dfs(start_board, 0, bound, path, visited)
        if t is True:
            end_time = time.perf_counter()
            return path, nodes_expanded, len(path), end_time - start_time, 0
        if t == float('inf'):
            return [], nodes_expanded, 0, time.perf_counter() - start_time, 0
        bound = t

def astar(start_board):
    start = copy.deepcopy(start_board)
    start_time = time.perf_counter()
    heap = []
    visited = set()
    path_map = {}
    cost_map = {}
    h = manhattan_distance(start)
    key = serialize(start)
    heapq.heappush(heap, (h, 0, start))
    visited.add(key)
    path_map[key] = []
    cost_map[key] = 0
    nodes_expanded = 0
    while heap:
        est_total, g, board = heapq.heappop(heap)
        key = serialize(board)
        nodes_expanded += 1
        if board == GOAL_STATE:
            end_time = time.perf_counter()
            solve_time = end_time - start_time
            path = path_map[key]
            total_cost = len(path)
            frontier_nodes = len(heap)
            return path, nodes_expanded, total_cost, solve_time, frontier_nodes
        br, bc = find_blank(board)
        for dr, dc in MOVES:
            nr, nc = br + dr, bc + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                new_board = copy.deepcopy(board)
                new_board[br][bc], new_board[nr][nc] = new_board[nr][nc], new_board[br][bc]
                new_key = serialize(new_board)
                if new_key not in visited or cost_map[new_key] > g + 1:
                    visited.add(new_key)
                    cost_map[new_key] = g + 1
                    new_path = path_map[key] + [(nr, nc)]
                    path_map[new_key] = new_path
                    h = manhattan_distance(new_board)
                    heapq.heappush(heap, (g + 1 + h, g + 1, new_board))
    end_time = time.perf_counter()
    return [], nodes_expanded, 0, end_time - start_time, 0

def beam_search(start_board, beam_width=3):
    start = copy.deepcopy(start_board)
    start_time = time.perf_counter()
    frontier = [(manhattan_distance(start), start, [])]
    visited = set()
    visited.add(serialize(start))
    nodes_expanded = 0
    while frontier:
        frontier.sort(key=lambda x: x[0])
        next_frontier = []
        for _, board, path in frontier[:beam_width]:
            if board == GOAL_STATE:
                end_time = time.perf_counter()
                return path, nodes_expanded, len(path), end_time - start_time, len(frontier)
            nodes_expanded += 1
            br, bc = find_blank(board)
            for dr, dc in MOVES:
                nr, nc = br + dr, bc + dc
                if 0 <= nr < 3 and 0 <= nc < 3:
                    new_board = copy.deepcopy(board)
                    new_board[br][bc], new_board[nr][nc] = new_board[nr][nc], new_board[br][bc]
                    new_key = serialize(new_board)
                    if new_key not in visited:
                        visited.add(new_key)
                        h = manhattan_distance(new_board)
                        next_frontier.append((h, new_board, path + [(nr, nc)]))
        frontier = next_frontier
    end_time = time.perf_counter()
    return [], nodes_expanded, 0, end_time - start_time, 0

def dijkstra(start_board):
    start = copy.deepcopy(start_board)
    visited = set()
    heap = []
    nodes_expanded = 0
    start_time = time.perf_counter()
    heapq.heappush(heap, (0, start, []))
    while heap:
        cost, board, path = heapq.heappop(heap)
        key = serialize(board)
        if key in visited:
            continue
        visited.add(key)
        nodes_expanded += 1
        if board == GOAL_STATE:
            end_time = time.perf_counter()
            solve_time = end_time - start_time
            frontier_nodes = len(heap)
            return path, nodes_expanded, cost, solve_time, frontier_nodes
        br, bc = find_blank(board)
        for dr, dc in MOVES:
            nr, nc = br + dr, bc + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                new_board = copy.deepcopy(board)
                new_board[br][bc], new_board[nr][nc] = new_board[nr][nc], new_board[br][bc]
                new_key = serialize(new_board)
                if new_key not in visited:
                    heapq.heappush(heap, (cost + 1, new_board, path + [(nr, nc)]))
    end_time = time.perf_counter()
    return [], nodes_expanded, 0, end_time - start_time, len(heap)

def bidirectional_search(start_board):
    start = copy.deepcopy(start_board)
    goal = copy.deepcopy(GOAL_STATE)
    start_key = serialize(start)
    goal_key = serialize(goal)
    if start_key == goal_key:
        return [], 0, 0, 0.0, 0
    forward_queue = deque([(start, [])])
    backward_queue = deque([(goal, [])])
    forward_visited = {start_key: []}
    backward_visited = {goal_key: []}
    nodes_expanded = 0
    start_time = time.perf_counter()
    while forward_queue and backward_queue:
        for _ in range(len(forward_queue)):
            board, path = forward_queue.popleft()
            nodes_expanded += 1
            br, bc = find_blank(board)
            for dr, dc in MOVES:
                nr, nc = br + dr, bc + dc
                if 0 <= nr < 3 and 0 <= nc < 3:
                    new_board = copy.deepcopy(board)
                    new_board[br][bc], new_board[nr][nc] = new_board[nr][nc], new_board[br][bc]
                    new_key = serialize(new_board)
                    if new_key not in forward_visited:
                        forward_visited[new_key] = path + [(nr, nc)]
                        forward_queue.append((new_board, path + [(nr, nc)]))
                        if new_key in backward_visited:
                            end_time = time.perf_counter()
                            solve_time = end_time - start_time
                            backward_path = backward_visited[new_key]
                            full_path = path + [(nr, nc)] + list(reversed(backward_path))
                            return full_path, nodes_expanded, len(full_path), solve_time, len(forward_queue) + len(backward_queue)
        for _ in range(len(backward_queue)):
            board, path = backward_queue.popleft()
            nodes_expanded += 1
            br, bc = find_blank(board)
            for dr, dc in MOVES:
                nr, nc = br + dr, bc + dc
                if 0 <= nr < 3 and 0 <= nc < 3:
                    new_board = copy.deepcopy(board)
                    new_board[br][bc], new_board[nr][nc] = new_board[nr][nc], new_board[br][bc]
                    new_key = serialize(new_board)
                    if new_key not in backward_visited:
                        backward_visited[new_key] = path + [(br, bc)]
                        backward_queue.append((new_board, path + [(br, bc)]))
                        if new_key in forward_visited:
                            end_time = time.perf_counter()
                            solve_time = end_time - start_time
                            forward_path = forward_visited[new_key]
                            full_path = forward_path + list(reversed(path + [(br, bc)]))
                            return full_path, nodes_expanded, len(full_path), solve_time, len(forward_queue) + len(backward_queue)
    end_time = time.perf_counter()
    return [], nodes_expanded, 0, end_time - start_time, len(forward_queue) + len(backward_queue)
