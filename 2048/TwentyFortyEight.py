#  Author: Kyle Tranfaglia
#  Title: PynacleGames - Game04 - 2048
#  Last updated:  02/20/25
#  Description: This program uses PyQt5 packages to build the game 2048
import sys
import os
import random
import copy
import csv
from datetime import datetime
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QVBoxLayout, QDialog, QLabel
from PyQt5.QtGui import QPainter, QFont, QColor, QBrush, QPen
from PyQt5.QtCore import Qt, QRect

# Set game specifications: window size, cell/grid size, cell count, and grid starting location
CELL_COUNT = 4
CELL_SIZE = 150
CELL_PADDING = 15
CORNER_RADIUS = 12
W_WIDTH = 800
W_HEIGHT = 800

# Calculate grid width and height
grid_width = CELL_COUNT * (CELL_SIZE + CELL_PADDING) - CELL_PADDING
grid_height = CELL_COUNT * (CELL_SIZE + CELL_PADDING) - CELL_PADDING

# Calculate centered origin
GRID_ORIGINX = (W_WIDTH - grid_width) // 2
GRID_ORIGINY = (W_HEIGHT - grid_height) // 2

border_color = QColor(30, 30, 30)  # Border color for grid elements

# Define colors for tiles based on their values
tile_colors = {
    0: QColor(50, 50, 50),  # Dark gray (empty tiles)
    2: QColor(238, 228, 218),  # Light beige
    4: QColor(235, 215, 185),  # Soft golden beige
    8: QColor(242, 177, 121),  # Warm orange
    16: QColor(245, 149, 99),  # Deep orange
    32: QColor(246, 124, 95),  # Fiery red-orange
    64: QColor(246, 94, 59),  # Bold red
    128: QColor(237, 207, 114),  # Bright gold
    256: QColor(237, 204, 97),  # Rich golden yellow
    512: QColor(237, 200, 80),  # Deep gold
    1024: QColor(237, 197, 63),  # Goldenrod
    2048: QColor(60, 179, 113),  # Emerald green
    4096: QColor(30, 144, 255),  # Vivid blue
    8192: QColor(138, 43, 226),  # Electric purple
}


# Determines text color based on tile value
def get_text_color(value):
    if value in (2, 4):
        return QColor(118, 112, 100)  # Dark brown
    return QColor(255, 255, 255)  # White for all others


#  Simulates a move on a given board without modifying the actual game state
def simulate_move(board, direction):
    temp_board = copy.deepcopy(board)  # Create a deep copy of the board to avoid modifying the original

    # Slides and merges a single row or column properly
    def slide_and_merge(row):
        new_row = [value for value in row if value != 0]  # Remove zeros (shift left)
        merged = []
        i = 0
        while i < len(new_row):
            if i < len(new_row) - 1 and new_row[i] == new_row[i + 1] and i not in merged:
                new_row[i] *= 2  # Merge tiles
                new_row.pop(i + 1)  # Remove merged tile
                merged.append(i)  # Mark as merged
            i += 1
        return new_row + [0] * (len(row) - len(new_row))  # Pad with zeros

    # Apply move based on direction
    if direction == Qt.Key_Left:
        for r in range(len(temp_board)):
            temp_board[r] = slide_and_merge(temp_board[r])

    elif direction == Qt.Key_Right:
        for r in range(len(temp_board)):
            temp_board[r] = slide_and_merge(temp_board[r][::-1])[::-1]  # Reverse, merge, then reverse back

    elif direction == Qt.Key_Up:
        for c in range(len(temp_board[0])):
            column = [temp_board[r][c] for r in range(len(temp_board))]
            new_column = slide_and_merge(column)
            for r in range(len(temp_board)):
                temp_board[r][c] = new_column[r]

    elif direction == Qt.Key_Down:
        for c in range(len(temp_board[0])):
            column = [temp_board[r][c] for r in range(len(temp_board))]
            new_column = slide_and_merge(column[::-1])[::-1]
            for r in range(len(temp_board)):
                temp_board[r][c] = new_column[r]

    return temp_board


#  Determines possible moves from the current board state
def get_possible_moves(board):
    moves = []
    for move in [Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down]:
        temp_board = copy.deepcopy(board)
        if simulate_move(temp_board, move):  # If board state changes, move is possible
            moves.append(move)
    return moves


#  Evaluates the monotonicity of the board (favoring tiles that decrease in order)
def calculate_monotonicity(board):
    score = 0
    for row in board:  # Check row-wise monotonicity
        for i in range(3):
            if row[i] >= row[i + 1]:
                score += row[i]
            else:
                score -= row[i + 1]  # Penalize disorder
    for col in range(4):  # Check column-wise monotonicity
        for i in range(3):
            if board[i][col] >= board[i + 1][col]:
                score += board[i][col]
            else:
                score -= board[i + 1][col]  # Penalize disorder
    return score


#  Evaluates the board based on potential merges
def calculate_merge_potential(board):
    score = 0
    for row in range(4):
        for col in range(3):  # Encourage merging
            if board[row][col] == board[row][col + 1]:
                score += board[row][col] * 2
            if board[col][row] == board[col + 1][row]:
                score += board[col][row] * 2
    return score


#  Evaluates the smoothness of the board (penalizing large jumps in tile values)
def calculate_smoothness(board):
    score = 0
    for row in range(4):  # Row-wise smoothness check
        for col in range(3):
            score -= abs(board[row][col] - board[row][col + 1])
    for col in range(4):  # Column-wise smoothness check
        for row in range(3):
            score -= abs(board[row][col] - board[row + 1][col])
    return score


#  Evaluates the overall board state using a weighted heuristic function
def evaluate(board):
    empty_cells = sum(row.count(0) for row in board)
    monotonicity = calculate_monotonicity(board)
    merge_potential = calculate_merge_potential(board)
    smoothness = calculate_smoothness(board)
    # max_tile = max(max(row) for row in board)
    weights = [6.4, 3.1, 3.7, 2.7]

    return ((weights[0] * empty_cells) + (weights[1] * monotonicity) +
            (weights[2] * merge_potential) + (weights[3] * smoothness))


#  Finds the best move based on heuristic evaluation
def find_best_move(board):
    best_move = None
    best_score = float('-inf')

    for move in get_possible_moves(board):
        new_board = simulate_move(board, move)

        if new_board == board:
            continue  # Skip invalid moves

        score = evaluate(new_board)  # Evaluate only one move ahead
        if score > best_score:
            best_score = score
            best_move = move

    return best_move


# Dialog box object to show high scores
class HighScoresDialog(QDialog):
    def __init__(self, parent, scores):
        super().__init__(parent)

        # Set window properties
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("High Scores")
        self.setStyleSheet("background-color: #B0B0B0;")
        self.setFixedSize(600, 600)

        layout = QVBoxLayout()

        # Title label
        title = QLabel("Top 10 Scores")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: Blue; text-decoration: underline;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Formatting description label
        description = QLabel("Score\t -- \tMoves\t -- \tDate\t -- \tTime")
        description.setStyleSheet("font-size: 24px; font-weight: bold; color: Black;")
        description.setAlignment(Qt.AlignCenter)
        layout.addWidget(description)

        # Display the scores
        for i, (score, moves, timestamp) in enumerate(scores, start=1):
            score_label = QLabel(f"{i}. {score} -- {moves} -- {timestamp}")
            score_label.setStyleSheet("font-size: 24px; color: black;")
            score_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(score_label)

        # Add an exit button
        exit_button = QPushButton("Close")
        exit_button.setStyleSheet("font-size: 18px; color: White; background-color: Red; padding: 9px;")
        exit_button.clicked.connect(self.close)
        exit_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(exit_button, alignment=Qt.AlignLeft)

        self.setLayout(layout)


# Main 2048 game class
class TwentyFortyEight(QWidget):
    def __init__(self):
        super().__init__()

        # Set game defaults
        self.moves = 0
        self.points = 0
        self.move_history = []
        self.save_move_history = True
        self.game_saved = False
        self.__board = [[0 for _ in range(CELL_COUNT)] for _ in range(CELL_COUNT)]

        self.initUI()  # Initialize window properties
        self.add_random_tile()  # Place first random tile
        self.add_random_tile()  # Place second random tile

        # Reset game button
        self.reset_button = QPushButton("Reset", self)
        self.reset_button.setGeometry(250, 15, 135, 50)
        self.reset_button.setStyleSheet("""QPushButton {background-color: #E66233 ;
                     border-radius: 5px; font-size: 20px; font-family: "Verdana"}""")
        self.reset_button.setCursor(Qt.PointingHandCursor)
        self.reset_button.clicked.connect(self.reset_game)

        # High score button
        self.high_score_button = QPushButton("High Scores", self)
        self.high_score_button.setGeometry(415, 15, 135, 50)
        self.high_score_button.setStyleSheet("""QPushButton {background-color: #E33266;
                     border-radius: 5px; font-size: 20px; font-family: "Verdana"}""")
        self.high_score_button.setCursor(Qt.PointingHandCursor)
        self.high_score_button.clicked.connect(self.display_high_scores)

        # AI solve button
        self.ai_solve_button = QPushButton("AI Solver", self)
        self.ai_solve_button.setGeometry(332, 735, 135, 50)
        self.ai_solve_button.setStyleSheet("""QPushButton {background-color: #E99999;
                             border-radius: 5px; font-size: 20px; font-family: "Verdana"}""")
        self.ai_solve_button.setCursor(Qt.PointingHandCursor)
        self.ai_solve_button.clicked.connect(self.greedy_ai)

        # Set up label to display winner at end of match
        self.result_label = QLabel("Game Over!", self)
        self.result_label.setGeometry(250, 730, 300, 50)  # Position near the bottom
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("""font-size: 36px; font-weight: bold; color: white;""")
        self.result_label.hide()

        # Moves label
        self.moves_label = QLabel("Moves: 0", self)
        self.moves_label.setGeometry(80, 20, 170, 50)
        self.moves_label.setStyleSheet("font-size: 24px; color: white; font-weight: bold;")

        # Score label
        self.score_label = QLabel("Score: 0", self)
        self.score_label.setGeometry(575, 20, 180, 50)
        self.score_label.setStyleSheet("font-size: 24px; color: white; font-weight: bold;")

        self.show()

    # Initialize game window properties
    def initUI(self):
        self.setWindowTitle('2048')
        self.setFixedSize(W_WIDTH, W_HEIGHT)
        self.setStyleSheet("background-color: #010101;")
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    # Render the game board and tiles
    def paintEvent(self, event):
        qp = QPainter(self)  # Create a QPainter instance for rendering

        with qp:
            # Iterate through each cell in the grid
            for row in range(CELL_COUNT):
                for col in range(CELL_COUNT):
                    value = self.__board[row][col]
                    color = tile_colors.get(value, QColor(50, 50, 50))

                    # Calculate tile position within the grid
                    x = GRID_ORIGINX + col * (CELL_SIZE + CELL_PADDING)
                    y = GRID_ORIGINY + row * (CELL_SIZE + CELL_PADDING)
                    cell_rect = QRect(x, y, CELL_SIZE, CELL_SIZE)  # Define tile rectangle

                    # Draw tile with rounded corners
                    qp.setBrush(QBrush(color))
                    qp.setPen(Qt.NoPen)  # Remove border outline
                    qp.drawRoundedRect(cell_rect, CORNER_RADIUS, CORNER_RADIUS)

                    # Draw tile value if it's not empty (0)
                    if value:
                        qp.setPen(get_text_color(value))
                        qp.setFont(QFont('Montserrat Bold', 32, QFont.Bold))
                        text = str(value)

                        # Calculate text width and height for proper centering
                        text_width = qp.fontMetrics().width(text)
                        text_height = qp.fontMetrics().height()

                        # Draw the tile value centered in the tile
                        qp.drawText((x + (CELL_SIZE - text_width) // 2),
                                    (y + (CELL_SIZE + text_height - CELL_PADDING) // 2), text)

    # Handle player input for movement
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
            self.move_tiles(event.key())
            self.update()
        elif event.key() == Qt.Key_Space:
            # Greedy algorithm
            self.greedy_ai()

    # Greedy algorithm to choose best move at the current state until game over
    def greedy_ai(self):
        while True:
            best_move = find_best_move(self.__board)  # Get best move
            if best_move:
                self.move_tiles(best_move)
                self.update()
            else:
                # Game over (no possible moves)
                self.reset_button.setText("Play Again")
                self.ai_solve_button.hide()
                self.result_label.show()
                break

    # Move and merge tiles based on input direction
    def move_tiles(self, direction):

        # Slide and merge tiles in a single row
        def slide(row):
            new_row = [value for value in row if value != 0]  # Remove empty tiles and shift values to the left
            i = 0
            while i < len(new_row) - 1:
                # Merge adjacent tiles if they have the same value
                if new_row[i] == new_row[i + 1]:
                    new_row[i] *= 2  # Double the tile value
                    self.points += new_row[i]  # Update score
                    self.moves += 1  # Increment move counter
                    self.move_history.append((self.moves, self.points))  # Store the move number and points
                    del new_row[i + 1]  # Remove merged tile
                    new_row.append(0)  # Append zero to keep length consistent
                i += 1
            return new_row + [0] * (CELL_COUNT - len(new_row))  # Return the processed row with zero-padding at the end

        rotated = False  # Track if board was transposed
        original_board = self.__board  # Store board state to track change

        # If moving up or down, transpose the board to treat columns as rows
        if direction in (Qt.Key_Up, Qt.Key_Down):
            self.__board = [list(x) for x in zip(*self.__board)]  # Transpose board
            rotated = True  # Mark as rotated

        # If moving right or down, reverse rows to work from right to left
        if direction in (Qt.Key_Right, Qt.Key_Down):
            self.__board = [list(reversed(row)) for row in self.__board]

        # Process each row to slide and merge tiles
        self.__board = [slide(row) for row in self.__board]

        # Reverse rows back if they were reversed earlier
        if direction in (Qt.Key_Right, Qt.Key_Down):
            self.__board = [list(reversed(row)) for row in self.__board]

        # If board was transposed, transpose it back to restore original structure
        if rotated:
            self.__board = [list(x) for x in zip(*self.__board)]

        # Check if the board has changed
        if original_board != self.__board:
            self.moves += 1  # Increment move count
            self.add_random_tile()  # Add a random tile

            # Update the score and move labels
            self.score_label.setText(f"Score: {self.points}")
            self.moves_label.setText(f"Moves: {self.moves}")
        else:
            # Check if there are any possible merges horizontally or vertically
            for r in range(CELL_COUNT):
                for c in range(CELL_COUNT):
                    # Check horizontal merge
                    if c < CELL_COUNT - 1 and self.__board[r][c] == self.__board[r][c + 1]:
                        return  # There's still a possible move (horizontal merge)
                    # Check vertical merge
                    if r < CELL_COUNT - 1 and self.__board[r][c] == self.__board[r + 1][c]:
                        return  # There's still a possible move (vertical merge)

            # Game over (no possible moves)
            self.reset_button.setText("Play Again")
            self.ai_solve_button.hide()
            self.result_label.show()

            # Save the score (one time only)
            if not self.game_saved:
                self.save_score()
                self.game_saved = True

    # Add a 2 or 4 tile in a random empty tile
    def add_random_tile(self):
        # Get a list of all empty tiles
        empty_cells = [(r, c) for r in range(CELL_COUNT) for c in range(CELL_COUNT) if self.__board[r][c] == 0]

        # Check if an empty tile exists
        if empty_cells:
            # Set a 2 or 4 tile in a random empty tile
            r, c = random.choice(empty_cells)
            self.__board[r][c] = 2 if random.random() < 0.9 else 4

    # Reset board and game variables
    def reset_game(self):
        # Save move and point history
        if self.save_move_history:
            self.save_move_history_to_csv()
        # Reset game variables
        self.moves = 0
        self.points = 0
        self.move_history = []
        self.save_move_history = False
        self.game_saved = False
        self.__board = [[0 for _ in range(CELL_COUNT)] for _ in range(CELL_COUNT)]

        # Reset text elements
        self.result_label.hide()
        self.ai_solve_button.show()
        self.score_label.setText("Score: 0")
        self.moves_label.setText("Moves: 0")

        # Reconfigure a random start state
        self.add_random_tile()
        self.add_random_tile()
        self.setFocus()
        self.update()

    # Save score and date/time in a txt file
    def save_score(self):
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d -- %H:%M:%S")
        with open("scores.txt", "a") as file:
            file.write(f"{self.points},{self.moves},{formatted_time}\n")

    # Load all scores and dates/times for score txt file and return a sorted list (descending)
    def load_scores(self):
        if not os.path.exists("scores.txt"):
            return []
        with open("scores.txt", "r") as file:
            scores = []
            # Parse the txt file to gather scores and dates/times
            for line in file:
                parts = line.strip().split(",")
                if len(parts) == 3 and parts[0].isdigit():
                    score = int(parts[0])
                    moves = int(parts[1])
                    timestamp = parts[2]
                    scores.append((score, moves, timestamp))
        return sorted(scores, key=lambda x: x[0], reverse=True)  # Return sorted list (descending) by score

    # Create the high scores dialog box and display the top ten high scores
    def display_high_scores(self):
        scores = self.load_scores()
        top_scores = scores[:10]
        dialog = HighScoresDialog(self, top_scores)
        dialog.exec_()

    # Save the move and point history for the game to a csv (overwrites)
    def save_move_history_to_csv(self, filename="moves.csv"):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Move Number", "Score"])  # CSV header

            # Write each move and the score
            for move, score in self.move_history:
                writer.writerow([move, score])
        print(f"Move history saved to {filename}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = TwentyFortyEight()
    sys.exit(app.exec_())
