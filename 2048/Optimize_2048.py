import random
from scipy.optimize import differential_evolution
from TwentyFortyEight import (simulate_move, get_possible_moves,
                              calculate_monotonicity, calculate_merge_potential, calculate_smoothness)


class Dummy2048Game:
    MAX_MOVES = 50  # Limit number of moves per game

    def __init__(self):
        self.moves = 0
        self.max_moves = self.MAX_MOVES  # Set move limit
        self.points = 0
        self.board = [[0] * 4 for _ in range(4)]
        self.add_random_tile()
        self.add_random_tile()

    def move_tiles(self, direction):
        new_board = simulate_move(self.board, direction)
        if new_board != self.board:
            self.board = new_board
            self.moves += 1
            self.add_random_tile()
            self.points += sum(sum(row) for row in self.board)

    def add_random_tile(self):
        empty_cells = [(r, c) for r in range(4) for c in range(4) if self.board[r][c] == 0]
        if empty_cells:
            r, c = random.choice(empty_cells)
            self.board[r][c] = 2 if random.random() < 0.9 else 4


def fitness(weights):
    print(f"Evaluating fitness for weights: {weights}")
    return -run_serial_games(weights)


def run_serial_games(weights, num_games=5):
    total_score = 0
    for game_index in range(num_games):
        print(f" Running game {game_index + 1}/{num_games}")
        game = Dummy2048Game()
        while game.moves < game.max_moves:
            best_move = find_best_move(game.board, weights)
            if best_move:
                game.move_tiles(best_move)
            else:
                break
        total_score += game.points
    return total_score / num_games


def optimize_weights():
    print("Starting optimization...")
    bounds = [(1, 5)] * 5  # Bounds for each weight
    result = differential_evolution(fitness, bounds, strategy='best1bin', maxiter=5, popsize=1, disp=True)
    print(f"Optimization completed. Best weights found: {result.x.tolist()}")
    return result.x.tolist()


def find_best_move(board, weights):
    best_move = None
    best_score = float('-inf')
    for move in get_possible_moves(board):
        new_board = simulate_move(board, move)
        max_tile = max(max(row) for row in new_board)
        if max_tile >= 2048:
            return move  # Immediate return if 2048 is reached
        score = evaluate_with_weights(new_board, weights)
        if score > best_score:
            best_score = score
            best_move = move
    return best_move


def evaluate_with_weights(board, weights):
    empty_cells = sum(row.count(0) for row in board)
    monotonicity = calculate_monotonicity(board)
    merge_potential = calculate_merge_potential(board)
    smoothness = calculate_smoothness(board)
    max_tile = max(max(row) for row in board)
    return (
            weights[0] * empty_cells +
            weights[1] * monotonicity +
            weights[2] * merge_potential +
            weights[3] * smoothness +
            weights[4] * max_tile
    )


if __name__ == "__main__":
    print("Running optimization for 2048 heuristic weights...")
    best_weights = optimize_weights()
    print("Optimized Weights:", best_weights)
