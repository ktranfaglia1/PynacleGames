#  Author: Kyle Tranfaglia
#  Title: PynacleGames - Game04 - 2048
#  Last updated:  03/01/25
#  Description: This program runs tests to optimize the weights for the AI evaluation parameters
""" This program adopts a simulated annealing strategy to search for a better set of heuristic weights. Rather than
adjusting one weight at a time, this approach perturbs all the weights simultaneously by adding a random change within
a specified range. After each perturbation, the new candidate weights are evaluated over several games to determine
their average performance. Unlike the original grid search, simulated annealing introduces a probabilistic acceptance
criterion: if the new candidate performs worse, it can still be accepted with a probability that decreases as the
temperature (a control parameter) lowers over time. This mechanism allows the algorithm to escape local optima early in
the process, gradually converging to a more optimal solution as the temperature cools. The refined balance between
exploration and exploitation, combined with the focus on average scores, offers a more robust search strategy, and the
best-found configuration is saved for further use. """
import random
import json
import math
from PyQt5.QtCore import Qt
from TwentyFortyEight import simulate_move, calculate_monotonicity, calculate_merge_potential, calculate_smoothness


# Simplified 2048 game environment for AI evaluation
class Dummy2048Game:
    def __init__(self):
        # Initialize a new dummy game with an empty board and two random tiles
        self.moves = 0
        self.points = 0
        self.board = [[0] * 4 for _ in range(4)]
        self.add_random_tile()
        self.add_random_tile()

    # Helper function that processes a row and returns both the new row and the merge score.
    def slide_and_merge_with_score(self, row):
        # Remove zeros (shift left)
        new_row = [value for value in row if value != 0]
        merge_score = 0
        i = 0
        while i < len(new_row) - 1:
            if new_row[i] == new_row[i + 1]:
                new_row[i] *= 2
                merge_score += new_row[i]  # Add the merged value to the score.
                del new_row[i + 1]
                new_row.append(0)  # Maintain row length.
            i += 1
        # Pad with zeros if needed.
        return new_row + [0] * (len(row) - len(new_row)), merge_score

    # Modified move_tiles that uses merge-aware scoring.
    def move_tiles(self, direction):
        original_board = [row[:] for row in self.board]  # Copy board for comparison.
        rotated = False
        # Transform board for vertical moves.
        if direction in (Qt.Key_Up, Qt.Key_Down):
            self.board = [list(x) for x in zip(*self.board)]
            rotated = True
        # Reverse rows for right or down moves.
        if direction in (Qt.Key_Right, Qt.Key_Down):
            self.board = [list(reversed(row)) for row in self.board]

        total_merge_score = 0
        new_board = []
        # Process each row using our helper.
        for row in self.board:
            merged_row, merge_score = self.slide_and_merge_with_score(row)
            new_board.append(merged_row)
            total_merge_score += merge_score

        self.board = new_board

        # Reverse earlier transformations.
        if direction in (Qt.Key_Right, Qt.Key_Down):
            self.board = [list(reversed(row)) for row in self.board]
        if rotated:
            self.board = [list(x) for x in zip(*self.board)]

        # Only update if the board has changed.
        if original_board != self.board:
            self.moves += 1
            self.points += total_merge_score  # Add only the merge scores.
            self.add_random_tile()

    # Adds a new tile (2 or 4) to a random empty cell on the board. 2 appears with 90% probability
    def add_random_tile(self):
        empty_cells = [(r, c) for r in range(4) for c in range(4) if self.board[r][c] == 0]
        if empty_cells:
            r, c = random.choice(empty_cells)
            self.board[r][c] = 2 if random.random() < 0.9 else 4


# Tests a set of weights by running multiple games and calculating the average score
def test_weights(weights, num_games=100):
    total_score = 0
    for game_index in range(num_games):
        print(f"Starting game {game_index + 1}/{num_games} with weights: {weights}")
        game = Dummy2048Game()
        move_count = 0
        while True:
            best_move = find_best_move(game.board, weights)
            if best_move:
                game.move_tiles(best_move)
                move_count += 1
                if move_count > 10000:  # Safety check to prevent infinite loops
                    print("ERROR: AI is taking too long. Breaking loop.")
                    break
            else:
                print(f"Game {game_index + 1} finished after {move_count} moves. Final Score: {game.points}")
                break
        total_score += game.points
    average_score = total_score / num_games
    print(f"Average Score for weights {weights}: {average_score}")
    with open("optimized_results_log_6.txt", "a") as log_file:
        log_file.write(f"Average Score for weights {weights}: {average_score}\n")
    return average_score


# Returns a list of possible moves for the current board state
def get_possible_moves(board):
    moves = []
    for move in [Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down]:
        if simulate_move(board, move) != board:  # Check if move would change the board
            moves.append(move)
    return moves


# Determines the best move based on the weighted evaluation function
def find_best_move(board, weights):
    best_move = None
    best_score = float('-inf')
    possible_moves = get_possible_moves(board)
    if not possible_moves:
        return None  # No valid moves available
    for move in possible_moves:
        new_board = simulate_move(board, move)
        score = evaluate_with_weights(new_board, weights)
        if score > best_score:
            best_score = score
            best_move = move
    return best_move


# Evaluates a board state using the weighted heuristic function
def evaluate_with_weights(board, weights):
    # Calculate various heuristics
    empty_cells = sum(row.count(0) for row in board)
    monotonicity = calculate_monotonicity(board)
    merge_potential = calculate_merge_potential(board)
    smoothness = calculate_smoothness(board)
    max_tile = max(max(row) for row in board)

    # Apply weights to each heuristic and return weighted sum
    return (
            weights[0] * empty_cells +  # Empty cells (space availability)
            weights[1] * monotonicity +  # Monotonicity (ordered tiles)
            weights[2] * merge_potential +  # Merge potential (adjacent same values)
            weights[3] * smoothness +  # Smoothness (gradual value changes)
            weights[4] * max_tile  # Maximum tile value
    )


# Applies constraints to keep weights within specified bounds
def apply_constraints(weight, min_val=0.0, max_val=10.0):
    return max(min_val, min(max_val, weight))


# Optimization Algorithm: Simulated Annealing
def optimize_weights_sa(initial_weights, num_iterations=400, num_games=30,
                        initial_temp=1.0, cooling_rate=0.9, step_size=0.5):
    """
    Optimizes weights using a simulated annealing approach.

    Parameters:
      initial_weights: List of starting weights.
      num_iterations: Number of iterations to run the annealing process.
      num_games: Number of games to average over for each evaluation.
      initial_temp: Starting temperature for annealing.
      cooling_rate: Factor by which temperature is reduced each iteration.
      step_size: Maximum change applied to each weight during a perturbation.
    """
    current_weights = list(initial_weights)
    best_weights = list(initial_weights)
    current_score = test_weights(current_weights, num_games=num_games)
    best_score = current_score
    current_temp = initial_temp

    print(f"Starting simulated annealing with initial weights: {initial_weights}, score: {current_score}")

    for iteration in range(num_iterations):
        # Create a new candidate by perturbing each weight randomly with constraints
        candidate_weights = []
        for w in current_weights:
            # Apply random perturbation
            new_w = w + random.uniform(-step_size, step_size)
            # Apply constraint to keep weight positive
            new_w = apply_constraints(new_w)
            candidate_weights.append(new_w)

        candidate_score = test_weights(candidate_weights, num_games=num_games)
        score_diff = candidate_score - current_score

        # Simulated annealing acceptance criterion:
        # 1. Always accept better solutions
        # 2. Sometimes accept worse solutions based on temperature
        if score_diff > 0 or random.random() < math.exp(score_diff / current_temp):
            current_weights = candidate_weights
            current_score = candidate_score
            # Update best weights and score if current solution is the best so far
            if candidate_score > best_score:
                best_weights = candidate_weights
                best_score = candidate_score

        print(f"Iteration {iteration + 1}/{num_iterations} -- Current Score: {current_score}, Best Score: {best_score}")
        current_temp *= cooling_rate  # Reduce temperature according to cooling schedule

    print(f"Optimized weights: {best_weights}, Best Average Score: {best_score}")
    with open("optimized_results_log_6.txt", "a") as log_file:  # Save results to text file
        log_file.write(f"Optimized weights: {best_weights}, Best Average Score: {best_score}\n")
    # Save optimization results to a JSON file
    with open("optimized_results_V2.json", "a") as file:
        file.write(json.dumps({"optimized_weights": best_weights, "best_score": best_score}) + "\n")
    print("Results saved to optimized_results_V2.json")
    return best_weights, best_score


if __name__ == "__main__":
    print("Running simulated annealing optimization for 2048 AI solver...")
    initial_weights = [6.226451613800638, 3.7328975401272255,
                       3.9499062708948642, 2.3864974450482634, 1.4422339807248714]  # Starting weights
    optimize_weights_sa(initial_weights)
