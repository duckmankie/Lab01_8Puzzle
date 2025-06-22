from collections import deque
import copy

def serialize(board):
    return tuple(val for row in board for val in row)

GOAL_STATE = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def bfs(start_board):
    start = copy.deepcopy(start_board)
    queue = deque([(start, [])])
    visited = set()
    visited.add(serialize(start))

    while queue:
        board, path = queue.popleft()
        if board == GOAL_STATE:
            return path

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
    return []

def dfs(start_board, max_depth=500):
    start = copy.deepcopy(start_board)
    visited = set()
    path = []

    def recursive_dfs(board, depth):
        if board == GOAL_STATE:
            return True
        if depth >= max_depth:
            return False

        key = serialize(board)
        visited.add(key)

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
    return path if found else []

def iddfs(start_board, max_depth=500):
    start = copy.deepcopy(start_board)

    def dls(board, depth_limit, path, visited):
        if board == GOAL_STATE:
            return path

        if len(path) >= depth_limit:
            return None

        key = serialize(board)
        visited.add(key)

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
            return result

    return []  # Không tìm thấy lời giải trong max_depth bước


def find_blank(board):
    for r in range(3):
        for c in range(3):
            if board[r][c] == 8:
                return r, c
    return None, None


import heapq

def ucs(start_board):
    start = copy.deepcopy(start_board)
    visited = set()
    heap = []
    
    # (cost, board, path)
    heapq.heappush(heap, (0, start, []))

    while heap:
        cost, board, path = heapq.heappop(heap)
        key = serialize(board)
        if key in visited:
            continue
        visited.add(key)

        if board == GOAL_STATE:
            return path

        br, bc = find_blank(board)
        for dr, dc in MOVES:
            nr, nc = br + dr, bc + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                new_board = copy.deepcopy(board)
                new_board[br][bc], new_board[nr][nc] = new_board[nr][nc], new_board[br][bc]
                new_key = serialize(new_board)
                if new_key not in visited:
                    heapq.heappush(heap, (cost + 1, new_board, path + [(nr, nc)]))

    return []  # không tìm thấy lời giải
