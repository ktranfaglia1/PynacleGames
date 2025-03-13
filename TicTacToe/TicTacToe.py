#  Author: Kyle Tranfaglia
#  Title: PynacleGames - Game03 - Tic-Tac-Toe
#  Last updated: 02/05/25
#  Description: This program uses PyQt5 packages to build the game Tic-Tac-Toe with AI players
import sys
import random
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QDialog, QVBoxLayout, QLabel

# Set game specifications: window size, cell/grid size, cell count, padding, and grid starting location
CELL_COUNT = 3
CELL_SIZE = 200
W_WIDTH = 800
W_HEIGHT = 800
GRID_ORIGINX = 100
GRID_ORIGINY = 100
PADDING = int(CELL_SIZE * 0.16)


# Dialogue box to display AI difficulties
class DifficultyDialog(QDialog):
    difficulty_selected = pyqtSignal(str)  # Define a custom signal to pass the selected difficulty

    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Difficulty Menu")
        self.setFixedSize(275, 275)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)  # Remove '?' button
        self.setStyleSheet("background-color: #444444;")

        # Layout setup
        layout = QVBoxLayout(self)

        # Title label
        title = QLabel("Choose a Difficulty", self)
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Local button
        local_button = QPushButton("Local", self)
        local_button.setStyleSheet(
            "background-color: #607D8B; color: white; padding: 8px; border-radius: 10px; font-size: 20px;")
        local_button.setCursor(Qt.PointingHandCursor)
        local_button.clicked.connect(lambda: self.set_difficulty("Local"))
        layout.addWidget(local_button)

        # Easy button
        easy_button = QPushButton("Easy", self)
        easy_button.setStyleSheet(
            "background-color: #4CAF50; color: white; padding: 8px; border-radius: 10px; font-size: 20px;")
        easy_button.setCursor(Qt.PointingHandCursor)
        easy_button.clicked.connect(lambda: self.set_difficulty("Easy"))
        layout.addWidget(easy_button)

        # Medium button
        medium_button = QPushButton("Medium", self)
        medium_button.setStyleSheet(
            "background-color: #FF9800; color: white; padding: 8px; border-radius: 10px; font-size: 20px;")
        medium_button.setCursor(Qt.PointingHandCursor)
        medium_button.clicked.connect(lambda: self.set_difficulty("Medium"))
        layout.addWidget(medium_button)

        # Hard button
        hard_button = QPushButton("Hard", self)
        hard_button.setStyleSheet(
            "background-color: #F44336; color: white; padding: 8px; border-radius: 10px; font-size: 20px;")
        hard_button.setCursor(Qt.PointingHandCursor)
        hard_button.clicked.connect(lambda: self.set_difficulty("Hard"))
        layout.addWidget(hard_button)

        self.setLayout(layout)

    # Set the difficulty in TicTacToe class by sending a signal with the updated difficulty
    def set_difficulty(self, difficulty):
        self.difficulty_selected.emit(difficulty)
        self.accept()


# Main class for Tic-tac-Toe game
class TicTacToe(QWidget):

    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle('TicTacToe')
        self.setFixedSize(W_WIDTH, W_HEIGHT)
        self.center_on_screen()
        self.setMouseTracking(True)

        # Set game defaults
        self.difficulty = "Medium"
        self.__turn = 0
        self.__winner = False
        self.__board = [[-1, -1, -1], [-1, -1, -1], [-1, -1, -1]]

        # Reset game button
        self.reset_button = QPushButton("Restart", self)
        self.reset_button.setGeometry(225, 20, 150, 55)
        self.reset_button.setStyleSheet("""QPushButton {background-color: #C81212;
               border-radius: 5px; font-size: 20px; font-family: "Verdana"}""")
        self.reset_button.setCursor(Qt.PointingHandCursor)
        self.reset_button.clicked.connect(self.reset_game)

        # Back to menu button
        self.menu_button = QPushButton("Menu", self)
        self.menu_button.setGeometry(425, 20, 150, 55)
        self.menu_button.setStyleSheet("""QPushButton {background-color: #4EB812;
                      border-radius: 5px; font-size: 20px; font-family: "Verdana"}""")
        self.menu_button.setCursor(Qt.PointingHandCursor)
        self.menu_button.clicked.connect(self.toggle_menu)

        # Set up label to display winner at end of match
        self.result_label = QLabel("", self)
        self.result_label.setGeometry(250, 730, 300, 50)  # Position near the bottom
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("""font-size: 36px; font-weight: bold; color: white;""")

        # Initialize menu
        self.menu_screen = None
        self.init_menu()

        self.show()

    # Creates the menu screen overlay
    def init_menu(self):
        # Initialize menu screen
        self.menu_screen = QWidget(self)
        self.menu_screen.setGeometry(0, 0, W_WIDTH, W_HEIGHT)
        self.menu_screen.setStyleSheet("background-color: rgba(0, 0, 0, 255);")

        # Set up a layout box for buttons and text
        layout = QVBoxLayout(self.menu_screen)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignCenter)

        # Set title
        title = QLabel("❌⭕❌\nTic-Tac-Toe\n⭕❌⭕", self)
        title.setStyleSheet("color: white; font-size: 48px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)

        # Play game button
        play_button = QPushButton("Play", self)
        play_button.setStyleSheet("font-size: 28px; color: White; background-color: Green; padding: 20px;"
                                  "border-radius: 18px; width: 200px;")
        play_button.setCursor(Qt.PointingHandCursor)
        play_button.clicked.connect(self.toggle_menu)

        # Open difficulty dialogue box button
        difficulty_button = QPushButton("Select Difficulty", self)
        difficulty_button.setStyleSheet("font-size: 28px; color: White; background-color: Blue; padding: 20px;"
                                        "border-radius: 18px; width: 200px;")
        difficulty_button.setCursor(Qt.PointingHandCursor)
        difficulty_button.clicked.connect(self.select_difficulty)

        # Exit application button
        exit_button = QPushButton("Exit", self)
        exit_button.setStyleSheet("font-size: 28px; color: White; background-color: Red; padding: 20px;"
                                  "border-radius: 18px; width: 200px;")
        exit_button.setCursor(Qt.PointingHandCursor)
        exit_button.clicked.connect(self.close)

        # Add everything to the layout
        layout.addWidget(title)
        layout.addSpacing(35)
        layout.addWidget(play_button)
        layout.addWidget(difficulty_button)
        layout.addWidget(exit_button)

        self.menu_screen.setLayout(layout)  # Enable the layout

    # Toggle the main menu screen
    def toggle_menu(self):
        if self.menu_screen.isVisible():
            self.menu_screen.hide()
        else:
            self.menu_screen.show()
            self.reset_game()

    # Open the difficulty selection dialog and set the difficulty
    def select_difficulty(self):
        dialog = DifficultyDialog()
        dialog.difficulty_selected.connect(self.set_difficulty)  # Connect the signal to set the difficulty
        dialog.exec_()

    # Set the difficulty with the emitted signal
    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        print(f"Selected difficulty: {self.difficulty}")

    # Center the application on the screen
    def center_on_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        center = screen.center()
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(center)
        self.move(frame_geometry.topLeft())

    # Draw the application upon initialization and update
    def paintEvent(self, event):
        # Set up painter object
        qp = QPainter()
        white_pen = QPen(QColor(225, 225, 225), 20, Qt.SolidLine, Qt.RoundCap)
        qp.begin(self)

        qp.fillRect(event.rect(), QColor(2, 2, 2))
        qp.setPen(white_pen)

        # Loop through the entire board and draw the updated board with all X's and O's
        for r in range(len(self.__board)):
            for c in range(len(self.__board[r])):
                qp.drawRect(GRID_ORIGINX + c * CELL_SIZE, GRID_ORIGINY + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                # Check if it's a winning square
                if self.__is_winning_square(r, c):
                    color = QColor(176, 38, 255)  # Winning color
                elif self.__board[r][c] == 0:
                    color = QColor(255, 0, 150)  # X color
                elif self.__board[r][c] == 1:
                    color = QColor(0, 255, 150)  # O color
                else:
                    color = None  # Empty tile, no drawing needed

                if color:  # If there is something to draw
                    qp.setPen(QPen(color, 20, Qt.SolidLine, Qt.RoundCap))
                    if self.__board[r][c] == 0:  # Draw X
                        qp.drawLine(GRID_ORIGINX + c * CELL_SIZE + PADDING, GRID_ORIGINY + r * CELL_SIZE + PADDING,
                                    GRID_ORIGINX + c * CELL_SIZE + CELL_SIZE - PADDING,
                                    GRID_ORIGINY + r * CELL_SIZE + CELL_SIZE - PADDING)
                        qp.drawLine(GRID_ORIGINX + c * CELL_SIZE + CELL_SIZE - PADDING,
                                    GRID_ORIGINY + r * CELL_SIZE + PADDING,
                                    GRID_ORIGINX + c * CELL_SIZE + PADDING,
                                    GRID_ORIGINY + r * CELL_SIZE + CELL_SIZE - PADDING)
                    elif self.__board[r][c] == 1:  # Draw O
                        qp.drawEllipse(GRID_ORIGINX + c * CELL_SIZE + PADDING, GRID_ORIGINY + r * CELL_SIZE + PADDING,
                                       CELL_SIZE - PADDING * 2, CELL_SIZE - PADDING * 2)
                qp.setPen(white_pen)  # Reset pen back to default

        # Check for winner and update reset button to say "Play Again"
        if self.__winner:
            self.reset_button.setText("Play Again")

        qp.end()

    # Handle mouse clicks
    def mousePressEvent(self, event):
        # Disable clicks (non-buttons) upon game end
        if self.__winner is True:
            return

        # Get the coordinates of the click
        row = (event.y() - GRID_ORIGINY) // CELL_SIZE
        col = (event.x() - GRID_ORIGINX) // CELL_SIZE

        # Check if the click is within the grid region
        if 0 <= row < CELL_COUNT and 0 <= col < CELL_COUNT:
            if self.__board[row][col] == -1:  # Make sure the tile is empty
                self.__board[row][col] = self.__turn
                self.__turn = (self.__turn + 1) % 2
        self.update()

        # Check for a draw
        if not self.get_possible_moves() and not self.__winner:
            self.result_label.setText("It's a Draw!")
            self.reset_button.setText("Play Again")

        # Play a bot move if there are empty tiles remaining
        if self.difficulty != "Local" and self.get_possible_moves():
            QTimer.singleShot(600, self.make_bot_move)  # Delay bot move to simulate thinking

    def make_bot_move(self):
        if self.__winner:  # Prevent the bot from moving after the game is won
            return
        # Executes the bot move after a delay
        if self.__turn == 1 and self.get_possible_moves():
            r, c = self.get_bot_move()
            self.__board[r][c] = self.__turn
            self.__turn = (self.__turn + 1) % 2
            self.update()

    # Check for a win by identifying winning tiles
    def __is_winning_square(self, r, c):
        for i in range(CELL_COUNT):
            # Row winner
            if self.__board[i][0] != -1 and self.__board[i][0] == self.__board[i][1] == self.__board[i][2]:
                self.__winner = True
                self.result_label.setText(f"{'X' if self.__board[i][0] == 0 else 'O'} Wins!")
                return r == i

            # Column winner
            if self.__board[0][i] != -1 and self.__board[0][i] == self.__board[1][i] == self.__board[2][i]:
                self.__winner = True
                self.result_label.setText(f"{'X' if self.__board[0][i] == 0 else 'O'} Wins!")
                return c == i

        # First diagonal winner
        if self.__board[0][0] != -1 and self.__board[0][0] == self.__board[1][1] == self.__board[2][2]:
            self.__winner = True
            self.result_label.setText(f"{'X' if self.__board[0][0] == 0 else 'O'} Wins!")
            return r == c

        # Second diagonal winner
        if self.__board[0][2] != -1 and self.__board[0][2] == self.__board[1][1] == self.__board[2][0]:
            self.__winner = True
            self.result_label.setText(f"{'X' if self.__board[0][2] == 0 else 'O'} Wins!")
            return r + c == 2

        return False

    # Handle mouse movement
    def mouseMoveEvent(self, event):
        # Get coordinates of mouse
        row = (event.y() - GRID_ORIGINY) // CELL_SIZE
        col = (event.x() - GRID_ORIGINX) // CELL_SIZE

        # Set cursor to pointer if over a valid location on the grid
        if 0 <= row < CELL_COUNT and 0 <= col < CELL_COUNT and self.__board[row][col] == -1 and self.__winner is False:
            self.setCursor(Qt.PointingHandCursor)  # Change cursor when hovering over an empty cell
        else:
            self.setCursor(Qt.ArrowCursor)  # Default cursor

    # Reset board and game variables
    def reset_game(self):
        self.__board = [[-1] * CELL_COUNT for _ in range(CELL_COUNT)]
        self.__turn = 0
        self.__winner = False
        self.reset_button.setText("Restart")
        self.result_label.setText("")
        self.update()

    # Get a bot move given bot difficulty
    def get_bot_move(self):
        if self.difficulty == "Easy":
            return self.get_random_move()
        elif self.difficulty == "Medium" or self.difficulty == "Hard":
            return self.get_good_move()

    # Get a list of all possible moves (empty tiles)
    def get_possible_moves(self):
        return [(r, c) for r in range(3) for c in range(3) if self.__board[r][c] == -1]

    # Check if a win will occur given a board position
    def check_win_condition(self):
        for i in range(CELL_COUNT):
            if self.__board[i][0] != -1 and self.__board[i][0] == self.__board[i][1] == self.__board[i][2]:
                return True
            if self.__board[0][i] != -1 and self.__board[0][i] == self.__board[1][i] == self.__board[2][i]:
                return True
        if self.__board[0][0] != -1 and self.__board[0][0] == self.__board[1][1] == self.__board[2][2]:
            return True
        if self.__board[0][2] != -1 and self.__board[0][2] == self.__board[1][1] == self.__board[2][0]:
            return True
        return False

    # Check if a move will result in a win
    def is_winning_move(self, move, player):
        # Temporarily place the move on the board  and Check if this move results in a win
        r, c = move
        self.__board[r][c] = player
        win = self.check_win_condition()
        self.__board[r][c] = -1  # Undo the move

        return win

    # Get a random legal move to play
    def get_random_move(self):
        empty_cells = self.get_possible_moves()
        return random.choice(empty_cells) if empty_cells else None

    # Get a logical move varying in optimality given bot difficulty
    def get_good_move(self):
        # Check if the bot can win
        for move in self.get_possible_moves():
            if self.is_winning_move(move, 1):
                return move

        # Block opponent’s winning move
        for move in self.get_possible_moves():
            if self.is_winning_move(move, 0):
                return move

        # Play optimal (non-trivial) move
        if self.difficulty == "Hard":
            # Take the center if available (the best strategic move)
            if self.__board[1][1] == -1:
                return 1, 1

            # Take a corner if available (strong second move)
            for corner in [(0, 0), (0, 2), (2, 0), (2, 2)]:
                if self.__board[corner[0]][corner[1]] == -1:
                    return corner

            # Take a side move if available
            for side in [(0, 1), (1, 0), (1, 2), (2, 1)]:
                if self.__board[side[0]][side[1]] == -1:
                    return side

        return self.get_random_move()  # Otherwise, pick a random move


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TicTacToe()
    sys.exit(app.exec_())
