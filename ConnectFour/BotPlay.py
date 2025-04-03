#  Author: Kyle Tranfaglia
#  Title: PynacleGames - Game05 - Connect Four
#  Last updated: 04/03/25
#  Description: This program runs test to play Connect Four bots against one another to test bot skill
import random
import math
import time
from datetime import datetime
import sys

# Constants for board size
ROWS = 6
COLS = 7

# Difficulties
DIFFICULTIES = ["Easy", "Medium", "Hard", "Master"]

# Bot origins
ORIGINAL = "Original"
UPDATED = "Updated"


class ConnectFourSimulator:
    def __init__(self, log_to_file=True, verbose=False):
        """
        Initialize the simulator
        """
        self.verbose = verbose
        self.log_to_file = log_to_file
        self.current_simulation_info = None

        if log_to_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_file = f"Connect_four_simulation_{timestamp}.txt"
            with open(self.log_file, "w") as f:
                f.write(f"Connect Four Bot Simulation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")

    def reset_board(self):
        """Initialize a new empty game board"""
        return [[0 for _ in range(COLS)] for _ in range(ROWS)]

    def log(self, message):
        """Log a message to console and/or file"""
        if self.verbose:
            print(message)

        if self.log_to_file:
            with open(self.log_file, "a") as f:
                f.write(message + "\n")

    def is_valid_move(self, board, col):
        """Check if a move is valid (column not full)"""
        return 0 <= col < COLS and board[0][col] == 0

    def get_next_open_row(self, board, col):
        """Find the next open row in the specified column"""
        for row in range(ROWS - 1, -1, -1):
            if board[row][col] == 0:
                return row
        return -1

    def drop_piece(self, board, col, player):
        """Drop a piece in the specified column for the specified player"""
        row = self.get_next_open_row(board, col)
        if row >= 0:
            board[row][col] = player
            return row
        return -1

    def check_win(self, board, row, col):
        """Check if the most recent move resulted in a win"""
        player = board[row][col]

        # Helper function to count connected pieces in a direction
        def count_in_direction(row_step, col_step):
            count = 0
            r, c = row, col
            while 0 <= r < ROWS and 0 <= c < COLS and board[r][c] == player:
                count += 1
                r += row_step
                c += col_step
            return count

        # Check all four directions
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # Vertical, Horizontal, Diagonals
        for r_step, c_step in directions:
            # Count in both positive and negative directions
            total = count_in_direction(r_step, c_step) + count_in_direction(-r_step, -c_step) - 1
            if total >= 4:
                return True
        return False

    def check_draw(self, board):
        """Check if the board is full (draw)"""
        return all(board[0][col] != 0 for col in range(COLS))

    def check_win_for_player(self, board, player):
        """Check if the specified player has won anywhere on the board"""
        # Check horizontal
        for row in range(ROWS):
            for col in range(COLS - 3):
                if all(board[row][col + i] == player for i in range(4)):
                    return True

        # Check vertical
        for col in range(COLS):
            for row in range(ROWS - 3):
                if all(board[row + i][col] == player for i in range(4)):
                    return True

        # Check positive diagonal
        for row in range(ROWS - 3):
            for col in range(COLS - 3):
                if all(board[row + i][col + i] == player for i in range(4)):
                    return True

        # Check negative diagonal
        for row in range(3, ROWS):
            for col in range(COLS - 3):
                if all(board[row - i][col + i] == player for i in range(4)):
                    return True

        return False

    def print_board(self, board):
        """Print the current board state to console (for debugging)"""
        for row in board:
            print("|", end=" ")
            for col in row:
                if col == 0:
                    print(".", end=" ")
                elif col == 1:
                    print("R", end=" ")
                elif col == 2:
                    print("Y", end=" ")
            print("|")
        print("+" + "-" * (COLS * 2 + 1) + "+")
        print("|", end=" ")
        for i in range(COLS):
            print(i, end=" ")
        print("|")
        print()

    def simulate_games(self, bot1_type, bot1_difficulty, bot2_type, bot2_difficulty, num_games=100):
        """
        Simulate games between two bots
        """
        # Statistics tracking
        bot1_wins = 0
        bot2_wins = 0
        draws = 0
        total_moves = 0

        # Store current simulation info
        self.current_simulation_info = {
            "red_type": bot1_type,
            "red_difficulty": bot1_difficulty,
            "yellow_type": bot2_type,
            "yellow_difficulty": bot2_difficulty
        }

        # Header for this set of games
        header = f"{bot1_type} {bot1_difficulty} (Red) vs {bot2_type} {bot2_difficulty} (Yellow)"
        separator = "=" * len(header)
        self.log(f"\n{separator}\n{header}\n{separator}\n")

        # Play games
        for game_num in range(1, num_games + 1):
            result = self.play_game(
                red_bot_type=bot1_type,
                red_bot_difficulty=bot1_difficulty,
                yellow_bot_type=bot2_type,
                yellow_bot_difficulty=bot2_difficulty
            )

            if result["winner"] == 1:
                bot1_wins += 1
                result_str = f"Red ({bot1_type} {bot1_difficulty}) won"
            elif result["winner"] == 2:
                bot2_wins += 1
                result_str = f"Yellow ({bot2_type} {bot2_difficulty}) won"
            else:
                draws += 1
                result_str = "Draw"

            total_moves += result["moves"]

            # Log the game result
            self.log(f"Game {game_num}: {result_str} in {result['moves']} moves. " +
                     f"Running score: Red {bot1_wins} - Yellow {bot2_wins} - Draws {draws}")

        # Calculate statistics
        avg_moves = total_moves / num_games if num_games > 0 else 0
        bot1_win_pct = (bot1_wins / num_games) * 100 if num_games > 0 else 0
        bot2_win_pct = (bot2_wins / num_games) * 100 if num_games > 0 else 0
        draw_pct = (draws / num_games) * 100 if num_games > 0 else 0

        # Log summary
        summary = [
            f"\nResults Summary:",
            f"Red ({bot1_type} {bot1_difficulty}): {bot1_wins} wins ({bot1_win_pct:.1f}%)",
            f"Yellow ({bot2_type} {bot2_difficulty}): {bot2_wins} wins ({bot2_win_pct:.1f}%)",
            f"Draws: {draws} ({draw_pct:.1f}%)",
            f"Average game length: {avg_moves:.1f} moves"
        ]

        for line in summary:
            self.log(line)

        return {
            "bot1_wins": bot1_wins,
            "bot2_wins": bot2_wins,
            "draws": draws,
            "avg_moves": avg_moves
        }

    def play_game(self, red_bot_type, red_bot_difficulty, yellow_bot_type, yellow_bot_difficulty):
        """
        Play a single game between two bots
        """
        # Initialize game state
        board = self.reset_board()
        current_player = 1  # 1 = Red, 2 = Yellow
        moves = 0
        winner = 0
        
        move_history = []

        # Main game loop
        while True:
            # Determine which bot is playing
            if current_player == 1:  # Red's turn
                bot_type = red_bot_type
                bot_difficulty = red_bot_difficulty
            else:  # Yellow's turn
                bot_type = yellow_bot_type
                bot_difficulty = yellow_bot_difficulty

            # self.print_board(board)

            # Get the bot's move
            col = self.get_bot_move(board, current_player, bot_type, bot_difficulty, move_history)
            
            # Debug invalid moves
            if not self.is_valid_move(board, col):
                self.log(f"ERROR: Bot {bot_type} {bot_difficulty} tried invalid move {col}")
                # Choose a random valid move instead
                valid_cols = [c for c in range(COLS) if self.is_valid_move(board, c)]
                if valid_cols:
                    col = random.choice(valid_cols)
                else:
                    # No valid moves left - must be a draw
                    break
            
            move_history.append(col)

            # Make the move
            row = self.drop_piece(board, col, current_player)
            if row == -1:
                # This should not happen if is_valid_move check passed
                self.log(f"ERROR: Failed to drop piece at column {col}")
                break
            
            moves += 1

            # Check for win/draw
            if self.check_win(board, row, col):
                winner = current_player
                break

            if self.check_draw(board):
                break

            # Switch players
            current_player = 3 - current_player  # 1 -> 2 or 2 -> 1

            # Safety measure: limit game length
            if moves >= 42:  # Maximum possible moves in Connect Four
                # Force a draw if we've reached the move limit
                winner = 0
                break

        return {
            "winner": winner,
            "moves": moves
        }

    def get_bot_move(self, board, player, bot_type, difficulty, move_history=None):
        """
        Get a move from a bot based on its type and difficulty
        """
        # Special case: for consistency in testing, always play center column first for human player
        if bot_type == ORIGINAL and len(move_history) == 0 and player == 1:
            return COLS // 2

        if bot_type == ORIGINAL:
            if difficulty == "Easy":
                return self.original_ai_easy(board, player)
            elif difficulty == "Medium":
                return self.original_ai_medium(board, player)
            elif difficulty == "Hard":
                return self.original_ai_hard(board, player)
            elif difficulty == "Master":
                return self.original_ai_master(board, player)
        elif bot_type == UPDATED:
            if difficulty == "Easy":
                return self.updated_ai_easy(board, player)
            elif difficulty == "Medium":
                return self.updated_ai_medium(board, player)
            elif difficulty == "Hard":
                return self.updated_ai_hard(board, player)
            elif difficulty == "Master":
                return self.updated_ai_master(board, player)

        # Default to random move if bot type/difficulty not recognized
        valid_columns = [col for col in range(COLS) if self.is_valid_move(board, col)]
        return random.choice(valid_columns) if valid_columns else -1

    # Original AI implementations

    def original_ai_easy(self, board, player):
        """Original Easy AI: Play randomly"""
        valid_columns = [col for col in range(COLS) if self.is_valid_move(board, col)]
        return random.choice(valid_columns) if valid_columns else -1

    def original_ai_medium(self, board, player):
        """Original Medium AI: Play winning move or block opponent"""
        valid_columns = [col for col in range(COLS) if self.is_valid_move(board, col)]
        if not valid_columns:
            return -1

        # Play winning move if possible
        for col in valid_columns:
            temp_board = [row[:] for row in board]  # Create a deep copy of the board
            row = self.drop_piece(temp_board, col, player)
            if row != -1 and self.check_win(temp_board, row, col):
                return col

        # Block opponent from winning
        opponent = 3 - player
        for col in valid_columns:
            temp_board = [row[:] for row in board]  # Create a deep copy of the board
            row = self.drop_piece(temp_board, col, opponent)
            if row != -1 and self.check_win(temp_board, row, col):
                return col

        # Play randomly as a last resort
        return random.choice(valid_columns)

    def original_ai_hard(self, board, player):
        """Original Hard AI: Minimax with depth 4"""
        return self.minimax_decision(board, player, depth=4, updated=False, master=False)

    def original_ai_master(self, board, player):
        """Original Master AI: Minimax with depth 6"""
        return self.minimax_decision(board, player, depth=6, updated=False, master=True)

    # Count the number of pieces on the board to determine move number
    def get_move_count(self, board):
        return sum(1 for row in board for cell in row if cell != 0)

    def minimax_decision(self, board, player, depth, updated, master):
        """Make a move using minimax with alpha-beta pruning"""
        move_count = self.get_move_count(board)  # Get move count for early game optimizations
        center_col = COLS // 2

        # First AI move
        if move_count < 3 and updated:
            return center_col

        valid_columns = [col for col in range(COLS) if self.is_valid_move(board, col)]
        if not valid_columns:
            return -1

        # Play winning move if possible
        for col in valid_columns:
            temp_board = [row[:] for row in board]
            row = self.drop_piece(temp_board, col, player)
            if row != -1 and self.check_win(temp_board, row, col):
                return col

        # Block opponent from winning
        opponent = 3 - player
        for col in valid_columns:
            temp_board = [row[:] for row in board]
            row = self.drop_piece(temp_board, col, opponent)
            if row != -1 and self.check_win(temp_board, row, col):
                return col

        if updated and master:
            # Then adjust based on game phase
            if move_count <= 8:  # Early game
                depth = 4
            elif move_count <= 20:  # Mid-game
                depth = 5
            else:  # Late game
                depth = 6

            # Order columns differently based on game phase
            if move_count <= 8:
                # Early game: heavily favor center and adjacent columns
                ordered_columns = sorted(valid_columns,
                                        key=lambda x: (
                                            -15 * (x == center_col),  # Center highest priority
                                            -8 * (abs(x - center_col) == 1),  # Adjacent to center
                                            -3 * (abs(x - center_col) == 2),  # Two away from center
                                            abs(x - center_col)  # Others by distance
                                        ))
            else:
                # Mid-late game: more balanced approach
                ordered_columns = sorted(valid_columns,
                                        key=lambda x: (
                                            -8 * (x == center_col),  # Center still important
                                            -4 * (abs(x - center_col) == 1),  # Adjacent still good
                                            abs(x - center_col)  # Others by distance
                                        ))
        else:
            # Order columns for prioritization: center and near-center moves
            ordered_columns = sorted(valid_columns,
                                    key=lambda x: -10 * (x == center_col) - 5 * (abs(x - center_col) == 1) + abs(x - center_col))

        # Find best move with minimax
        best_col = ordered_columns[0]  # Default to first column
        best_score = -math.inf
        best_columns = []  # For ties

        for col in ordered_columns:
            temp_board = [row[:] for row in board]
            row = self.drop_piece(temp_board, col, player)
            if row == -1:
                continue
                
            # Player is maximizing
            score = self.minimax(temp_board, depth - 1, -math.inf, math.inf, False, player)

            # Keep track of best score and ties
            if score > best_score:
                best_score = score
                best_columns = [col]
                best_col = col
            elif score == best_score:
                best_columns.append(col)  # Column with equal score

        # If we have multiple "best" columns, select the one closest to center
        if len(best_columns) > 1:
            best_col = min(best_columns, key=lambda x: abs(x - center_col))

        return best_col

    def minimax(self, board, depth, alpha, beta, maximizing, player):
        """Minimax algorithm with alpha-beta pruning"""
        opponent = 3 - player
        
        # Terminal state checks
        if self.check_win_for_player(board, player):
            return 10000  # Player wins
        if self.check_win_for_player(board, opponent):
            return -10000  # Opponent wins
        if self.check_draw(board):
            return 0  # Draw
        if depth == 0:
            return self.evaluate_board(board, player)

        valid_columns = [col for col in range(COLS) if self.is_valid_move(board, col)]
        
        if maximizing:  # Player's turn
            value = -math.inf
            for col in valid_columns:
                temp_board = [row[:] for row in board]
                row = self.drop_piece(temp_board, col, player)
                if row == -1:
                    continue
                    
                new_score = self.minimax(temp_board, depth - 1, alpha, beta, False, player)
                value = max(value, new_score)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:  # Opponent's turn
            value = math.inf
            for col in valid_columns:
                temp_board = [row[:] for row in board]
                row = self.drop_piece(temp_board, col, opponent)
                if row == -1:
                    continue
                    
                new_score = self.minimax(temp_board, depth - 1, alpha, beta, True, player)
                value = min(value, new_score)
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value

    def evaluate_board(self, board, player):
        """Evaluate the board from the perspective of the specified player"""
        score = 0
        opponent = 3 - player

        # Center column preference
        center_col = COLS // 2
        center_count = sum(1 for row in range(ROWS) if board[row][center_col] == player)
        score += center_count * 6

        # Count pieces and give bonus for pieces in lower rows
        for r in range(ROWS):
            row_bonus = ROWS - r  # Higher bonus for lower rows
            for c in range(COLS):
                if board[r][c] == player:
                    score += row_bonus // 4  # Small bonus for lower pieces

        # Evaluate all possible windows of 4
        for r in range(ROWS):
            for c in range(COLS - 3):  # Horizontal windows
                window = [board[r][c+i] for i in range(4)]
                score += self.evaluate_window(window, player, opponent)
                
        for r in range(ROWS - 3):
            for c in range(COLS):  # Vertical windows
                window = [board[r+i][c] for i in range(4)]
                score += self.evaluate_window(window, player, opponent)
                
        for r in range(ROWS - 3):
            for c in range(COLS - 3):  # Positive diagonal windows
                window = [board[r+i][c+i] for i in range(4)]
                score += self.evaluate_window(window, player, opponent)
                
        for r in range(3, ROWS):
            for c in range(COLS - 3):  # Negative diagonal windows
                window = [board[r-i][c+i] for i in range(4)]
                score += self.evaluate_window(window, player, opponent)

        return score

    def evaluate_window(self, window, player, opponent):
        """Evaluate a window of 4 positions"""
        player_count = window.count(player)
        opponent_count = window.count(opponent)
        empty_count = window.count(0)

        # Score based on game theory of Connect Four
        if player_count == 4:
            return 1000  # Win
        elif player_count == 3 and empty_count == 1:
            return 50   # Threat
        elif player_count == 2 and empty_count == 2:
            return 10   # Potential

        # Defensive scoring
        if opponent_count == 4:
            return -1000  # Loss
        elif opponent_count == 3 and empty_count == 1:
            return -50    # Opponent threat
        elif opponent_count == 2 and empty_count == 2:
            return -10    # Opponent potential

        # Add a small preference for lower positions
        return 0

    # Updated AI implementations

    def updated_ai_easy(self, board, player):
        """Updated Easy AI: Play randomly"""
        return self.original_ai_easy(board, player)

    def updated_ai_medium(self, board, player):
        """Updated Medium AI: Play winning move or block opponent"""
        return self.original_ai_medium(board, player)

    def updated_ai_hard(self, board, player):
        """Updated Hard AI: Enhanced minimax with depth 4"""
        return self.minimax_decision(board, player, depth=4, updated=True, master=False)

    def updated_ai_master(self, board, player):
        """Updated Master AI: Enhanced minimax with depth 6"""
        return self.minimax_decision(board, player, depth=6, updated=True, master=True)


def test_bots(bot1_type, bot1_difficulty, bot2_type, bot2_difficulty, num_games=50, swap_players=True, log_to_file=True, verbose=True):
    """
    Simple function to test two specific bots against each other
    """
    simulator = ConnectFourSimulator(log_to_file=log_to_file, verbose=verbose)
    
    start_time = time.time()
    
    # Store results
    results = {
        "bot1_wins_as_red": 0,
        "bot2_wins_as_yellow": 0,
        "bot1_wins_as_yellow": 0,
        "bot2_wins_as_red": 0,
        "draws": 0,
        "total_games": 0
    }
    
    # First configuration: Bot1 as red, Bot2 as yellow
    result1 = simulator.simulate_games(bot1_type, bot1_difficulty, bot2_type, bot2_difficulty, num_games)
    
    results["bot1_wins_as_red"] = result1["bot1_wins"]
    results["bot2_wins_as_yellow"] = result1["bot2_wins"]
    results["draws"] += result1["draws"]
    results["total_games"] += num_games
    
    # Second configuration: Bot2 as red, Bot1 as yellow (if swap_players is True)
    if swap_players:
        result2 = simulator.simulate_games(bot2_type, bot2_difficulty, bot1_type, bot1_difficulty, num_games)
        
        results["bot2_wins_as_red"] = result2["bot1_wins"]
        results["bot1_wins_as_yellow"] = result2["bot2_wins"]
        results["draws"] += result2["draws"]
        results["total_games"] += num_games
    
    # Calculate totals
    bot1_total_wins = results["bot1_wins_as_red"] + results["bot1_wins_as_yellow"]
    bot2_total_wins = results["bot2_wins_as_red"] + results["bot2_wins_as_yellow"]
    draws = results["draws"]
    total_games = results["total_games"]
    
    # Print overall summary
    total_time = time.time() - start_time
    simulator.log("\n" + "=" * 50)
    simulator.log("OVERALL TEST RESULTS")
    simulator.log("=" * 50)
    
    # Display detailed results
    simulator.log(f"\n{bot1_type} {bot1_difficulty}:")
    simulator.log(f"  Total wins: {bot1_total_wins} out of {total_games} games ({bot1_total_wins/total_games*100:.1f}%)")
    if swap_players:
        simulator.log(f"  Wins as Red: {results['bot1_wins_as_red']} out of {num_games} games ({results['bot1_wins_as_red']/num_games*100:.1f}%)")
        simulator.log(f"  Wins as Yellow: {results['bot1_wins_as_yellow']} out of {num_games} games ({results['bot1_wins_as_yellow']/num_games*100:.1f}%)")
    else:
        simulator.log(f"  Wins as Red: {results['bot1_wins_as_red']} out of {num_games} games ({results['bot1_wins_as_red']/num_games*100:.1f}%)")
    
    simulator.log(f"\n{bot2_type} {bot2_difficulty}:")
    simulator.log(f"  Total wins: {bot2_total_wins} out of {total_games} games ({bot2_total_wins/total_games*100:.1f}%)")
    if swap_players:
        simulator.log(f"  Wins as Red: {results['bot2_wins_as_red']} out of {num_games} games ({results['bot2_wins_as_red']/num_games*100:.1f}%)")
        simulator.log(f"  Wins as Yellow: {results['bot2_wins_as_yellow']} out of {num_games} games ({results['bot2_wins_as_yellow']/num_games*100:.1f}%)")
    else:
        simulator.log(f"  Wins as Yellow: {results['bot2_wins_as_yellow']} out of {num_games} games ({results['bot2_wins_as_yellow']/num_games*100:.1f}%)")
    
    simulator.log(f"\nDraws: {draws} out of {total_games} games ({draws/total_games*100:.1f}%)")
    simulator.log(f"Total testing time: {total_time:.1f} seconds")
    
    return results


def main():
    # Test same difficulty levels (hard)
    test_bots(
        bot1_type=ORIGINAL,
        bot1_difficulty="Hard",
        bot2_type=ORIGINAL, 
        bot2_difficulty="Hard", 
        num_games=3,
        swap_players=True
    )
    
    # Test Original Hard vs Updated Hard
    test_bots(
        bot1_type=ORIGINAL,
        bot1_difficulty="Hard",
        bot2_type=UPDATED, 
        bot2_difficulty="Hard", 
        num_games=3,
        swap_players=True
    )
    
    # Test master difficulty
    test_bots(
        bot1_type=ORIGINAL,
        bot1_difficulty="Master",
        bot2_type=UPDATED, 
        bot2_difficulty="Master", 
        num_games=3,
        swap_players=True
    )

    # Test same difficulty levels (easy)
    test_bots(
        bot1_type=ORIGINAL,
        bot1_difficulty="Easy",
        bot2_type=ORIGINAL, 
        bot2_difficulty="Easy", 
        num_games=500,
        swap_players=True
    )


# This special guard helps PyCharm understand this isn't a pytest file
if __name__ == "__main__":
    main()