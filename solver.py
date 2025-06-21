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

def dfs(start_board, max_depth=30):
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

def find_blank(board):
    for r in range(3):
        for c in range(3):
            if board[r][c] == 8:
                return r, c
    return None, None
