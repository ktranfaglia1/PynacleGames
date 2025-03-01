#  Author: Kyle Tranfaglia
#  Title: PynacleGames - Game04 - 2048
#  Last updated:  02/20/25
#  Description: This program runs tests to optimize the weights for the AI evaluation parameters
""" The original optimization program implements a straightforward grid search technique for tuning the heuristic
weights used by the greedy AI solver for 2048. In this approach, the algorithm begins with a base set of weights and
evaluates the AI's performance by running multiple games—calculating the average score as the evaluation metric. It
then iteratively perturbs each weight individually by a small fixed step (both positively and negatively) and retests
the modified set. If any perturbation leads to an improvement in the average score, that set of weights is adopted as
the new best configuration. This process is repeated for all weights, and the final optimized set is saved to a results
file. While simple to implement, this method can be limited by its inability to escape local optima and by the fact
that it adjusts only one parameter at a time. """
import random
import json
from PyQt5.QtCore import Qt
from TwentyFortyEight import (simulate_move, calculate_monotonicity, calculate_merge_potential, calculate_smoothness)


# A simplified dummy 2048 game environment for AI evaluation
class Dummy2048Game:
    def __init__(self):
        self.moves = 0
        self.points = 0
        self.board = [[0] * 4 for _ in range(4)]
        self.add_random_tile()
        self.add_random_tile()

    # Moves tiles in the given direction and adds a random tile if the move is valid
    def move_tiles(self, direction):
        new_board = simulate_move(self.board, direction)
        if new_board != self.board:
            self.board = new_board
            self.moves += 1
            self.add_random_tile()
            self.points += sum(sum(row) for row in self.board)

    # Adds a new tile (either 2 or 4) in a random empty cell
    def add_random_tile(self):
        empty_cells = [(r, c) for r in range(4) for c in range(4) if self.board[r][c] == 0]
        if empty_cells:
            r, c = random.choice(empty_cells)
            self.board[r][c] = 2 if random.random() < 0.9 else 4


# Runs multiple games and returns an evaluation score
def test_weights(weights, num_games=100):
    total_score = 0
    max_tiles_reached = []

    for game_index in range(num_games):
        print(f"Starting game {game_index + 1}/{num_games} with weights: {weights}")
        game = Dummy2048Game()
        move_count = 0

        while True:
            best_move = find_best_move(game.board, weights)
            if best_move:
                game.move_tiles(best_move)
                move_count += 1
                if move_count > 10000:  # Prevent infinite loops
                    print("ERROR: AI is taking too long. Breaking loop.")
                    break
            else:
                print(f"Game {game_index + 1} finished after {move_count} moves. Final Score: {game.points}")
                break

        max_tile = max(max(row) for row in game.board)
        max_tiles_reached.append(max_tile)
        total_score += game.points

    return total_score / num_games


# Performs weight optimization using a simple grid search by perturbing each weight
def optimize_weights_by_perturbation(base_weights, step=.05):
    """Performs a simple grid search by perturbing each weight up and down."""
    best_weights = list(base_weights)
    best_score = test_weights(base_weights)

    print(f"Base weights: {base_weights}, Score: {best_score}")

    for i in range(len(base_weights)):
        for delta in [-step, step]:  # Test -0.5 and +0.5 changes
            new_weights = list(base_weights)
            new_weights[i] += delta  # Modify one weight

            score = test_weights(new_weights)
            print(f"Testing {new_weights} -> Score: {score}")

            if score > best_score:  # If it's better, update
                best_score = score
                best_weights = new_weights

    print(f"Optimized weights: {best_weights}, Best Score: {best_score}")
    # Save results to a file
    with open("optimized_results.json", "a") as file:
        file.write(json.dumps({"optimized_weights": best_weights, "best_score": best_score}) + "\n")

    print("Results saved to optimized_results.json")


# Returns a list of possible moves based on the current board state
def get_possible_moves(board):
    moves = []
    for move in [Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down]:
        if simulate_move(board, move) != board:  # Check if move changes the board
            moves.append(move)
    return moves


# Determines the best move based on the evaluation function
def find_best_move(board, weights):
    best_move = None
    best_score = float('-inf')
    possible_moves = get_possible_moves(board)

    if not possible_moves:
        return None  # No moves available

    for move in possible_moves:
        new_board = simulate_move(board, move)
        score = evaluate_with_weights(new_board, weights)
        if score > best_score:
            best_score = score
            best_move = move

    return best_move


# Evaluates the given board state using weighted heuristics
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
    print("Running weight perturbation optimization for 2048 AI solver...")
    initial_weights = [2.5, 2.4, 2.5, 2, 4.05]  # Starting weights
    optimize_weights_by_perturbation(initial_weights)
