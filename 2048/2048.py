#  Author: Kyle Tranfaglia
#  Title: PynacleGames - Game04 - 2048
#  Last updated:  02/07/25
#  Description: This program uses PyQt5 packages to build the game 2048
import sys
import os
import random
from datetime import datetime
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QVBoxLayout, QDialog, QLabel
from PyQt5.QtGui import QPainter, QFont, QColor, QPainterPath, QBrush, QPen
from PyQt5.QtCore import Qt, QRect

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

border_color = QColor(30, 30, 30)

tile_colors = {
    0: QColor(50, 50, 50),  # Dark gray (empty tiles)
    2: QColor(238, 228, 218),  # Light beige (better contrast with white)
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


def get_text_color(value):
    if value in (2, 4):
        return QColor(118, 112, 100)  # Dark brown for better contrast
    return QColor(255, 255, 255)  # White for all others


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


class TwentyFortyEight(QWidget):
    def __init__(self):
        super().__init__()
        self.moves = 0
        self.points = 0
        self.game_saved = False
        self.__board = [[0 for _ in range(CELL_COUNT)] for _ in range(CELL_COUNT)]
        self.initUI()
        self.add_random_tile()
        self.add_random_tile()

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

        # Set up label to display winner at end of match
        self.result_label = QLabel("", self)
        self.result_label.setGeometry(250, 730, 300, 50)  # Position near the bottom
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("""font-size: 36px; font-weight: bold; color: white;""")

        self.show()

    def initUI(self):
        self.setWindowTitle('2048')
        self.setFixedSize(W_WIDTH, W_HEIGHT)
        self.setStyleSheet("background-color: #010101;")
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def paintEvent(self, event):
        qp = QPainter(self)
        with qp:
            for row in range(CELL_COUNT):
                for col in range(CELL_COUNT):
                    value = self.__board[row][col]
                    color = tile_colors.get(value, QColor(50, 50, 50))

                    # Calculate cell position and size with padding
                    x = GRID_ORIGINX + col * (CELL_SIZE + CELL_PADDING)
                    y = GRID_ORIGINX + row * (CELL_SIZE + CELL_PADDING)
                    cell_rect = QRect(x, y, CELL_SIZE, CELL_SIZE)

                    # Draw the rounded rectangle (cell)
                    qp.setBrush(QBrush(color))
                    qp.setPen(Qt.NoPen)
                    qp.drawRoundedRect(cell_rect, CORNER_RADIUS, CORNER_RADIUS)

                    if value:
                        qp.setPen(get_text_color(value))
                        qp.setFont(QFont('Montserrat Bold', 36, QFont.Bold))
                        text = str(value)
                        text_width = qp.fontMetrics().width(text)
                        text_height = qp.fontMetrics().height()
                        qp.drawText((x + (CELL_SIZE - text_width) // 2),
                                    (y + (CELL_SIZE + text_height - CELL_PADDING) // 2), text)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
            self.move_tiles(event.key())
            self.add_random_tile()
            self.update()

    def move_tiles(self, direction):

        def slide(row):
            new_row = [value for value in row if value != 0]
            i = 0
            while i < len(new_row) - 1:
                if new_row[i] == new_row[i + 1]:
                    new_row[i] *= 2
                    self.points += new_row[i]
                    self.moves += 1
                    del new_row[i + 1]
                    new_row.append(0)
                i += 1
            return new_row + [0] * (CELL_COUNT - len(new_row))

        rotated = False

        if direction in (Qt.Key_Up, Qt.Key_Down):
            self.__board = [list(x) for x in zip(*self.__board)]  # Transpose
            rotated = True

        if direction in (Qt.Key_Right, Qt.Key_Down):
            self.__board = [list(reversed(row)) for row in self.__board]

        self.__board = [slide(row) for row in self.__board]

        if direction in (Qt.Key_Right, Qt.Key_Down):
            self.__board = [list(reversed(row)) for row in self.__board]

        if rotated:
            self.__board = [list(x) for x in zip(*self.__board)]  # Transpose back

    def add_random_tile(self):
        empty_cells = [(r, c) for r in range(CELL_COUNT) for c in range(CELL_COUNT) if self.__board[r][c] == 0]

        if empty_cells:
            r, c = random.choice(empty_cells)
            self.__board[r][c] = 2 if random.random() < 0.9 else 4
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
            self.result_label.setText("Game Over!")
            if not self.game_saved:
                self.save_score()
                self.game_saved = True

    def reset_game(self):
        self.moves = 0
        self.points = 0
        self.game_saved = False
        self.__board = [[0 for _ in range(CELL_COUNT)] for _ in range(CELL_COUNT)]
        self.result_label.setText("")
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = TwentyFortyEight()
    sys.exit(app.exec_())
