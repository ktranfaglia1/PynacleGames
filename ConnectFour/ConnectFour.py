#  Author: Kyle Tranfaglia
#  Title: PynacleGames - Game05 - Connect Four
#  Last updated: 03/12/25
#  Description: This program uses PyQt5 packages to build the game Connect Four with many AI bots of various strength
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QDialog, QVBoxLayout
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

# Constants for board size and appearance
ROWS = 6
COLS = 7
W_WIDTH = 800
W_HEIGHT = 800
SPACING = 12
TILE_SIZE = 96


# Dialogue box to display AI difficulties
class DifficultyDialog(QDialog):
    difficulty_selected = pyqtSignal(str)  # Define a custom signal to pass the selected difficulty

    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Difficulty Menu")
        self.setFixedSize(250, 250)
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


# Main Connect Four game class
class ConnectFour(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connect Four")
        self.setFixedSize(W_WIDTH, W_HEIGHT)
        self.setStyleSheet("background-color: #010101;")
        self.setMouseTracking(True)

        # Initialize game state
        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.current_player = 1  # 1 for Red, 2 for Yellow
        self.selected_col = -1  # Track the column the mouse is hovering over
        self.win_flag = 0  # 0 = No win, 1 = Red wins, 2 = Yellow wins
        self.difficulty = "Medium"

        # Pre-calculate offsets
        self.offset_x = (W_WIDTH - (TILE_SIZE * COLS)) // 2
        self.offset_y = (W_HEIGHT - (TILE_SIZE * ROWS)) // 2

        # Initialize animation
        self.animating = False
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_piece)
        self.animation_current_row = -1
        self.animation_target_row = None
        self.animation_col = None

        # Game board color
        self.board_color = QColor(0, 70, 160)

        # Set up label to display winner at end of match
        self.result_label = QLabel("", self)
        self.result_label.setGeometry(200, 730, 400, 40)
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("""font-size: 36px; font-weight: bold; color: white;""")

        # Menu Button (Bottom Left)
        self.menu_button = QPushButton("Menu", self)
        self.menu_button.setGeometry(52, 720, 135, 50)
        self.menu_button.setStyleSheet("font-size: 20px; font-weight: bold; border-radius: 5px;"
                                       "background-color: gray; color: white;")
        self.menu_button.setCursor(Qt.PointingHandCursor)
        self.menu_button.clicked.connect(self.toggle_menu)

        # Restart Button (Bottom Right)
        self.restart_button = QPushButton("Restart", self)
        self.restart_button.setGeometry(W_WIDTH - 187, 720, 135, 50)
        self.restart_button.setStyleSheet("font-size: 20px; font-weight: bold; border-radius: 5px;"
                                          "background-color: gray; color: white;")
        self.restart_button.setCursor(Qt.PointingHandCursor)
        self.restart_button.clicked.connect(self.reset_game)

        # Initialize menu
        self.menu_screen = None
        self.init_menu()

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
        title = QLabel("🔴🔴🔴🔴\nConnect Four\n🟡🟡🟡🟡", self)
        title.setStyleSheet("color: white; font-size: 48px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)

        # Play game button
        play_button = QPushButton("Play", self)
        play_button.setStyleSheet("font-size: 28px; color: White; background-color: #E53935; padding: 20px;"
                                  "border-radius: 18px; width: 200px;")
        play_button.setCursor(Qt.PointingHandCursor)
        play_button.clicked.connect(self.toggle_menu)

        # Open difficulty dialogue box button
        difficulty_button = QPushButton("Select Difficulty", self)
        difficulty_button.setStyleSheet("font-size: 28px; color: White; background-color: #FFC107; padding: 20px;"
                                        "border-radius: 18px; width: 200px;")
        difficulty_button.setCursor(Qt.PointingHandCursor)
        difficulty_button.clicked.connect(self.select_difficulty)

        # Exit application button
        exit_button = QPushButton("Exit", self)
        exit_button.setStyleSheet("font-size: 28px; color: White; background-color: #455A64; padding: 20px;"
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

    # Drop a piece on the game board that falls to the lowest valid row in a column
    def drop_piece(self, col):
        # Do nothing if an animation is in progress or if the game is over
        if self.animating or self.win_flag != 0:
            return

        # Check for valid column
        if 0 <= col < COLS:
            # Find the lowest empty row in this column
            target_row = None
            for row in reversed(range(ROWS)):
                if self.board[row][col] == 0:
                    target_row = row
                    break

            if target_row is None:
                return  # Column is full

            # Set up animation parameters:
            self.animating = True
            self.animation_col = col
            self.animation_target_row = target_row
            self.animation_current_row = -1  # Start above the board
            self.animation_timer.start(50)  # Update every x ms

    # Animate pieces falling into place by quickly updating the board as the row decrements
    def animate_piece(self):
        self.animation_current_row += 1
        self.update()

        # Check if animation has reached its target
        if self.animation_current_row >= self.animation_target_row:
            self.animation_timer.stop()
            self.animating = False
            self.board[self.animation_target_row][self.animation_col] = self.current_player

            # Check for win or draw
            if self.check_win(self.animation_target_row, self.animation_col):
                self.win_flag = self.current_player
                self.result_label.setText("Red Player Wins!" if self.current_player == 1 else "Yellow Player Wins!")
            elif self.check_draw():
                self.win_flag = -1
                self.result_label.setText("It's a Draw!")
            else:
                self.current_player = 3 - self.current_player

    # Draw the game board
    def draw_board(self, qp):
        # Draw the board background
        qp.setBrush(QBrush(self.board_color))
        qp.setPen(Qt.NoPen)
        qp.drawRect(self.offset_x - SPACING, self.offset_y - SPACING,
                    COLS * TILE_SIZE + SPACING * 2, ROWS * TILE_SIZE + SPACING * 2)

        # Draw the preview piece if game is active
        if self.win_flag == 0 and self.selected_col >= 0 and (
                not self.animating or self.selected_col != self.animation_col):
            preview_color = QColor(224, 0, 0) if self.current_player == 1 else QColor(224, 224, 0)
            qp.setBrush(QBrush(preview_color))
            qp.drawEllipse(self.selected_col * TILE_SIZE + self.offset_x + int(SPACING / 2),
                           self.offset_y - TILE_SIZE - 5, TILE_SIZE - SPACING, TILE_SIZE - SPACING)

        # Draw the board cells and already placed pieces
        for row in range(ROWS):
            for col in range(COLS):
                x, y = col * TILE_SIZE + self.offset_x, row * TILE_SIZE + self.offset_y

                # Draw the empty circles (holes in the board)
                qp.setBrush(QBrush(QColor(0, 0, 0)))
                qp.drawEllipse(x + int(SPACING / 2), y + int(SPACING / 2),
                               TILE_SIZE - SPACING, TILE_SIZE - SPACING)

                # Draw the pieces that are already on the board
                if self.board[row][col] == 1:
                    qp.setBrush(QBrush(QColor(224, 0, 0)))  # Red
                    qp.drawEllipse(x + int(SPACING / 2), y + int(SPACING / 2),
                                   TILE_SIZE - SPACING, TILE_SIZE - SPACING)
                elif self.board[row][col] == 2:
                    qp.setBrush(QBrush(QColor(224, 224, 0)))  # Yellow
                    qp.drawEllipse(x + int(SPACING / 2), y + int(SPACING / 2),
                                   TILE_SIZE - SPACING, TILE_SIZE - SPACING)

        # Draw the animated falling piece (if one is active)
        if self.animating:
            x = self.animation_col * TILE_SIZE + self.offset_x + int(SPACING / 2)

            # Calculate y position - if above the board, draw it above
            if self.animation_current_row < 0:
                y = self.offset_y - TILE_SIZE + int(SPACING / 2)
            else:
                y = self.animation_current_row * TILE_SIZE + self.offset_y + int(SPACING / 2)

            # Use the current player's color for the falling piece
            if self.current_player == 1:
                qp.setBrush(QBrush(QColor(224, 0, 0)))  # Red
            else:
                qp.setBrush(QBrush(QColor(224, 224, 0)))  # Yellow

            qp.drawEllipse(x, y, TILE_SIZE - SPACING, TILE_SIZE - SPACING)

    # Check if the current move results in a win
    def check_win(self, row, col):
        player = self.board[row][col]

        def count_in_direction(row_step, col_step):
            count = 0
            r, c = row, col
            while 0 <= r < ROWS and 0 <= c < COLS and self.board[r][c] == player:
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

    # Check if the board is full and no more moves are possible
    def check_draw(self):
        return all(0 not in row for row in self.board)

    # Determine the column index based on mouse x-coordinate
    def get_column_from_position(self, x):
        if self.offset_x <= x <= self.offset_x + TILE_SIZE * COLS:
            col = (x - self.offset_x) // TILE_SIZE
            return max(0, min(COLS - 1, col))
        return -1

    # Handle mouse movement to highlight hovered column
    def mouseMoveEvent(self, event):
        new_col = self.get_column_from_position(event.x())
        if new_col != self.selected_col:  # Update only if column changes
            self.selected_col = new_col
            self.update()

    # Handle mouse clicks to place pieces
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.win_flag == 0:
            col = self.get_column_from_position(event.x())
            if col >= 0:
                self.drop_piece(col)

    # Render the game board and pieces
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.draw_board(qp)
        qp.end()

    # Reset the game to its initial state
    def reset_game(self):
        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.current_player = 1
        self.selected_col = -1
        self.win_flag = 0
        self.result_label.setText("")
        self.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = ConnectFour()
    game.show()
    sys.exit(app.exec_())
