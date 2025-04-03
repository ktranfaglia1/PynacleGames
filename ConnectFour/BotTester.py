import sys
import random
import time
import math
from datetime import datetime

# Import the necessary classes from the existing programs
# Note: We're importing the ConnectFour class, but we'll only use its AI functions
from ConnectFour import ConnectFour as CF1
from OriginalConnectFour import ConnectFour as CF2

# Constants for board size (same as in the original programs)
ROWS = 6
COLS = 7


class AITester:
    def __init__(self, ai1_type, ai1_version, ai2_type, ai2_version, num_games=100):
        self.ai1_type = ai1_type  # Type of AI for Player 1 (e.g., "Easy", "Medium", etc.)
        self.ai1_version = ai1_version  # Version of the program (1 for ConnectFour.py, 2 for OriginalConnectFour.py)
        self.ai2_type = ai2_type  # Type of AI for Player 2
        self.ai2_version = ai2_version  # Version of the program for Player 2
        self.num_games = num_games  # Number of games to play (per player order)

        # Initialize game statistics
        self.stats = {
            "ai1_wins": 0,
            "ai2_wins": 0,
            "draws": 0,
            "total_moves": 0,
            "games_played": 0
        }

        # Create instances of both Connect Four games for their AI functions
        self.cf1 = CF1()  # From ConnectFour.py
        self.cf2 = CF2()  # From OriginalConnectFour.py

        # Log file for results
        self.log_file = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def log(self, message):
        """Log message to both console and the log file"""
        print(message)
        if self.log_file:
            self.log_file.write(message + "\n")

    def setup_log_file(self, swap=False):
        """Set up or update the log file with header information"""
        if not self.log_file:
            filename = f"ai_test_{self.ai1_type}v{self.ai1_version}_vs_{self.ai2_type}v{self.ai2_version}_{self.timestamp}.txt"
            self.log_file = open(filename, "w")

        # Write header
        player_red = f"{self.ai2_type} (v{self.ai2_version})" if swap else f"{self.ai1_type} (v{self.ai1_version})"
        player_yellow = f"{self.ai1_type} (v{self.ai1_version})" if swap else f"{self.ai2_type} (v{self.ai2_version})"

        header = f"Connect Four AI Testing\n"
        header += f"{'=' * 50}\n"
        header += f"Red Player (1): {player_red}\n"
        header += f"Yellow Player (2): {player_yellow}\n"
        header += f"Number of games: {self.num_games}\n"
        header += f"{'=' * 50}\n\n"

        self.log(header)

    def create_board(self):
        """Create an empty Connect Four board"""
        return [[0 for _ in range(COLS)] for _ in range(ROWS)]

    def is_valid_move(self, board, col):
        """Check if a move is valid (column has empty slots)"""
        return board[0][col] == 0

    def get_next_open_row(self, board, col):
        """Get the next open row in the given column"""
        for row in reversed(range(ROWS)):
            if board[row][col] == 0:
                return row
        return -1  # Column is full (shouldn't happen if is_valid_move is checked)

    def make_move(self, board, col, player):
        """Make a move on the board"""
        row = self.get_next_open_row(board, col)
        if row != -1:
            board[row][col] = player
            return row
        return -1

    def check_win(self, board, row, col, player):
        """Check if the current move results in a win (copied from the original code)"""

        def count_in_direction(row_step, col_step):
            count = 0
            r, c = row, col
            while 0 <= r < ROWS and 0 <= c < COLS and board[r][c] == player:
                count += 1
                r += row_step
                c += col_step
            return count

        # Check in all four possible directions
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # Vertical, Horizontal, Diagonal
        for r_step, c_step in directions:
            total = count_in_direction(r_step, c_step) + count_in_direction(-r_step, -c_step) - 1
            if total >= 4:
                return True
        return False

    def check_draw(self, board):
        """Check if the board is full (draw)"""
        return all(board[0][col] != 0 for col in range(COLS))

    def get_ai_move(self, board, player, ai_type, ai_version):
        """Get a move from the specified AI"""
        # Create a temporary instance of the appropriate game class with the current board state
        if ai_version == 1:
            game_instance = self.cf1
        else:
            game_instance = self.cf2

        # Set the current board state and player
        game_instance.board = [row[:] for row in board]  # Copy the board
        game_instance.current_player = player
        game_instance.difficulty = ai_type

        # Get valid columns
        valid_columns = [col for col in range(COLS) if self.is_valid_move(board, col)]
        if not valid_columns:
            return -1  # No valid moves

        if ai_type == "Easy":
            # Easy AI makes random moves
            return random.choice(valid_columns)

        elif ai_type == "Medium":
            # First check for winning move
            for col in valid_columns:
                row = self.get_next_open_row(board, col)
                if row != -1:
                    board[row][col] = player
                    win = self.check_win(board, row, col, player)
                    board[row][col] = 0  # Undo move
                    if win:
                        return col

            # Then check for blocking opponent's winning move
            opponent = 3 - player
            for col in valid_columns:
                row = self.get_next_open_row(board, col)
                if row != -1:
                    board[row][col] = opponent
                    win = self.check_win(board, row, col, opponent)
                    board[row][col] = 0  # Undo move
                    if win:
                        return col

            # Otherwise random
            return random.choice(valid_columns)

        elif ai_type == "Hard" or ai_type == "Master":
            # For Hard and Master, use the minimax algorithm from the respective game

            # Set the difficulty to match the requested depth
            depth = 4 if ai_type == "Hard" else 6

            # Now find the best move using minimax
            best_col = valid_columns[0]  # Default
            best_score = -math.inf

            # Order columns (similar to how the original games do it)
            center_col = COLS // 2
            ordered_columns = sorted(valid_columns,
                                     key=lambda x: -10 * (x == center_col) - 5 * (abs(x - center_col) == 1) + abs(
                                         x - center_col))

            # For each possible move, evaluate using minimax
            for col in ordered_columns:
                row = self.get_next_open_row(board, col)
                board[row][col] = player

                # Use the appropriate minimax function
                if ai_version == 1:
                    # Version 1 minimax
                    memo = {}
                    score = game_instance.minimax_with_memo(depth, -math.inf, math.inf, False, memo)
                else:
                    # Version 2 minimax
                    memo = {}
                    score = game_instance.minimax_with_memo(depth, -math.inf, math.inf, False, memo)

                board[row][col] = 0  # Undo move

                if score > best_score:
                    best_score = score
                    best_col = col

            return best_col

        return random.choice(valid_columns)  # Default to random move if AI type not recognized

    # Simulate a single game between the two AIs
    def play_game(self, ai1_plays_red=True):
        board = self.create_board()
        current_player = 1  # Red goes first
        moves = 0
        game_result = {"winner": None, "moves": 0}

        # Map players to AIs
        if ai1_plays_red:
            player_mapping = {
                1: {"type": self.ai1_type, "version": self.ai1_version},  # Red
                2: {"type": self.ai2_type, "version": self.ai2_version}  # Yellow
            }
        else:
            player_mapping = {
                1: {"type": self.ai2_type, "version": self.ai2_version},  # Red
                2: {"type": self.ai1_type, "version": self.ai1_version}  # Yellow
            }

        # Game loop
        while True:
            # Get AI move
            ai_info = player_mapping[current_player]
            col = self.get_ai_move(board, current_player, ai_info["type"], ai_info["version"])

            if col == -1:  # No valid moves
                game_result["winner"] = 0  # Draw
                break

            # Make the move
            row = self.make_move(board, col, current_player)
            moves += 1

            # Check for win
            if self.check_win(board, row, col, current_player):
                game_result["winner"] = current_player
                break

            # Check for draw
            if self.check_draw(board):
                game_result["winner"] = 0  # Draw
                break

            # Switch player
            current_player = 3 - current_player

        # Record game statistics
        game_result["moves"] = moves
        return game_result

    # Run a set of games and record statistics
    def run_games(self, swap_players=False):
        # Set up the log file with the current player configuration
        self.setup_log_file(swap=swap_players)

        # Reset statistics
        local_stats = {
            "ai1_wins": 0,
            "ai2_wins": 0,
            "draws": 0,
            "total_moves": 0,
            "games_played": 0
        }

        # Run games
        for game_num in range(1, self.num_games + 1):
            start_time = time.time()

            # Play the game
            game_result = self.play_game(ai1_plays_red=not swap_players)

            # Update statistics
            local_stats["games_played"] += 1
            local_stats["total_moves"] += game_result["moves"]

            if game_result["winner"] == 0:
                local_stats["draws"] += 1
                result_str = "Draw"
            else:
                # Determine which AI won based on the current configuration
                if (game_result["winner"] == 1 and not swap_players) or (game_result["winner"] == 2 and swap_players):
                    local_stats["ai1_wins"] += 1
                    result_str = f"{self.ai1_type} (v{self.ai1_version}) wins"
                else:
                    local_stats["ai2_wins"] += 1
                    result_str = f"{self.ai2_type} (v{self.ai2_version}) wins"

            # Update global statistics
            for key in local_stats:
                self.stats[key] += local_stats[key]

            # Log the game result
            elapsed = time.time() - start_time
            self.log(f"Game {game_num}: {result_str} in {game_result['moves']} moves ({elapsed:.2f}s)")

            # Log running totals every 10 games
            if game_num % 10 == 0 or game_num == self.num_games:
                ai1_name = f"{self.ai1_type} (v{self.ai1_version})"
                ai2_name = f"{self.ai2_type} (v{self.ai2_version})"

                self.log(f"\nRunning Totals (Games 1-{game_num}):")
                self.log(
                    f"  {ai1_name}: {local_stats['ai1_wins']} wins ({local_stats['ai1_wins'] / game_num * 100:.1f}%)")
                self.log(
                    f"  {ai2_name}: {local_stats['ai2_wins']} wins ({local_stats['ai2_wins'] / game_num * 100:.1f}%)")
                self.log(f"  Draws: {local_stats['draws']} ({local_stats['draws'] / game_num * 100:.1f}%)")
                self.log(f"  Average moves per game: {local_stats['total_moves'] / game_num:.1f}")
                self.log(f"{'-' * 50}\n")

        return local_stats

    # Run all tests with both player configurations and print final results
    def run_all_tests(self):
        # First configuration: AI1 as Red, AI2 as Yellow
        self.log(
            f"Starting test series: {self.ai1_type} (v{self.ai1_version}) vs {self.ai2_type} (v{self.ai2_version})")
        config1_stats = self.run_games(swap_players=False)

        # Second configuration: AI2 as Red, AI1 as Yellow
        self.log(f"\nSwapping players for second series\n")
        config2_stats = self.run_games(swap_players=True)

        # Print final summary
        self.log("\n" + "=" * 50)
        self.log("FINAL RESULTS")
        self.log("=" * 50)

        ai1_name = f"{self.ai1_type} (v{self.ai1_version})"
        ai2_name = f"{self.ai2_type} (v{self.ai2_version})"

        total_games = self.stats["games_played"]

        self.log(f"Total Games Played: {total_games}")
        self.log(f"{ai1_name} Wins: {self.stats['ai1_wins']} ({self.stats['ai1_wins'] / total_games * 100:.1f}%)")
        self.log(f"{ai2_name} Wins: {self.stats['ai2_wins']} ({self.stats['ai2_wins'] / total_games * 100:.1f}%)")
        self.log(f"Draws: {self.stats['draws']} ({self.stats['draws'] / total_games * 100:.1f}%)")
        self.log(f"Average Moves Per Game: {self.stats['total_moves'] / total_games:.1f}")

        # Games with AI1 as Red
        red_win_rate = config1_stats["ai1_wins"] / self.num_games * 100
        self.log(
            f"\nWhen {ai1_name} plays as Red: {config1_stats['ai1_wins']}/{self.num_games} wins ({red_win_rate:.1f}%)")

        # Games with AI1 as Yellow
        yellow_win_rate = config2_stats["ai1_wins"] / self.num_games * 100
        self.log(
            f"When {ai1_name} plays as Yellow: {config2_stats['ai1_wins']}/{self.num_games} wins ({yellow_win_rate:.1f}%)")

        # Advantage of going first
        first_move_advantage = abs(
            red_win_rate - (100 - yellow_win_rate - (config2_stats["draws"] / self.num_games * 100)))
        self.log(f"\nFirst-Move Advantage: {first_move_advantage:.1f}%")

        # Close the log file
        if self.log_file:
            self.log_file.close()


def main():
    # Parameters: ai1_type, ai1_version, ai2_type, ai2_version, num_games
    tester = AITester("Hard", 1, "Hard", 2, 20)
    tester.run_all_tests()

    # # Run multiple tests with different configurations...
    # tester = AITester("Master", 1, "Master", 2, 20)
    # tester.run_all_tests()


if __name__ == "__main__":
    main()