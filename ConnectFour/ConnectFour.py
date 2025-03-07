#  Author: Kyle Tranfaglia
#  Title: PynacleGames - Game05 - Connect Four
#  Last updated: 03/06/25
#  Description: This program uses PyQt5 packages to build the game Connect Four with many AI bots of various strength
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtCore import Qt

# Constants for board size and appearance
ROWS = 6
COLS = 7
W_WIDTH = 800
W_HEIGHT = 800
SPACING = 12
TILE_SIZE = 96


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

        # Pre-calculate offsets
        self.offset_x = (W_WIDTH - (TILE_SIZE * COLS)) // 2
        self.offset_y = (W_HEIGHT - (TILE_SIZE * ROWS)) // 2

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

        # Restart Button (Bottom Right)
        self.restart_button = QPushButton("Restart", self)
        self.restart_button.setGeometry(W_WIDTH - 187, 720, 135, 50)
        self.restart_button.setStyleSheet("font-size: 20px; font-weight: bold; border-radius: 5px;"
                                          "background-color: gray; color: white;")
        self.restart_button.setCursor(Qt.PointingHandCursor)
        self.restart_button.clicked.connect(self.reset_game)

    # Attempt to drop a piece in the selected column
    def drop_piece(self, col):
        if 0 <= col < COLS:
            for row in reversed(range(ROWS)):  # Start checking from bottom row
                if self.board[row][col] == 0:
                    self.board[row][col] = self.current_player  # Place piece

                    # Check for win condition
                    if self.check_win(row, col):
                        self.win_flag = self.current_player
                        self.result_label.setText("Red Player Wins!" if self.win_flag == 1 else "Yellow Player Wins!")
                    elif self.check_draw():  # Check for a draw
                        self.win_flag = -1  # Indicate draw
                        self.result_label.setText("It's a Draw!")
                    else:
                        self.current_player = 3 - self.current_player  # Switch turn
                    self.update()
                    return

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

    # Draw the board and pieces
    def draw_board(self, qp):
        # Draw board background
        qp.setBrush(QBrush(self.board_color))
        qp.setPen(Qt.NoPen)
        qp.drawRect(self.offset_x - SPACING, self.offset_y - SPACING, COLS * TILE_SIZE + SPACING * 2,
                    ROWS * TILE_SIZE + SPACING * 2)

        # Highlight hovered column
        if self.selected_col >= 0:
            preview_color = QColor(224, 0, 0) if self.current_player == 1 else QColor(224, 224, 0)
            qp.setBrush(QBrush(preview_color))
            qp.drawEllipse(self.selected_col * TILE_SIZE + self.offset_x + int(SPACING / 2),
                           self.offset_y - TILE_SIZE - 5, TILE_SIZE - SPACING, TILE_SIZE - SPACING)

        # Draw board holes and pieces
        for row in range(ROWS):
            for col in range(COLS):
                x, y = col * TILE_SIZE + self.offset_x, row * TILE_SIZE + self.offset_y

                if self.board[row][col] == 1:
                    qp.setBrush(QBrush(QColor(224, 0, 0)))
                elif self.board[row][col] == 2:
                    qp.setBrush(QBrush(QColor(224, 224, 0)))
                else:
                    qp.setBrush(QBrush(QColor(0, 0, 0)))
                    qp.drawEllipse(x + int(SPACING / 2), y + int(SPACING / 2), TILE_SIZE - SPACING, TILE_SIZE - SPACING)
                    continue
                qp.drawEllipse(x + int(SPACING / 2), y + int(SPACING / 2), TILE_SIZE - SPACING, TILE_SIZE - SPACING)

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
