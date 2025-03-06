import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen
from PyQt5.QtCore import Qt

ROWS = 6
COLS = 7
W_WIDTH = 800
W_HEIGHT = 800
SPACING = 12  # Spacing constant for easy alterations
TILE_SIZE = 96  # Tile (circle) size constant


class ConnectFour(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connect Four")
        self.setFixedSize(W_WIDTH, W_HEIGHT)
        self.setStyleSheet("background-color: #010101;")
        self.setMouseTracking(True)  # Enable mouse tracking

        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.current_player = 1  # 1 for Red, 2 for Yellow
        self.selected_col = -1  # Track the column the mouse is hovering over

        # Pre-calculate offsets
        self.offset_x = (W_WIDTH - (TILE_SIZE * COLS)) // 2
        self.offset_y = (W_HEIGHT - (TILE_SIZE * ROWS)) // 2

        # Game board color
        self.board_color = QColor(0, 70, 160)  # Blue color for the board

    def drop_piece(self, col):
        if 0 <= col < COLS:
            for row in reversed(range(ROWS)):
                if self.board[row][col] == 0:
                    self.board[row][col] = self.current_player
                    self.current_player = 3 - self.current_player  # Switch player
                    self.update()
                    return

    def get_column_from_position(self, x):
        if self.offset_x <= x <= self.offset_x + TILE_SIZE * COLS:
            col = (x - self.offset_x) // TILE_SIZE
            return max(0, min(COLS - 1, col))
        return -1

    def mouseMoveEvent(self, event):
        new_col = self.get_column_from_position(event.x())
        if new_col != self.selected_col:  # Update only if column changes
            self.selected_col = new_col
            self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            col = self.get_column_from_position(event.x())
            if col >= 0:
                self.drop_piece(col)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.draw_board(qp)
        qp.end()

    def draw_board(self, qp):
        # Draw blue game board background
        board_width = COLS * TILE_SIZE
        board_height = ROWS * TILE_SIZE
        qp.setBrush(QBrush(self.board_color))
        qp.setPen(Qt.NoPen)  # No border for the board
        qp.drawRect(self.offset_x, self.offset_y, board_width, board_height)

        # Highlight the column being hovered over with player's color
        if self.selected_col >= 0:
            highlight_x = self.selected_col * TILE_SIZE + self.offset_x + int(SPACING / 2)

            # Set color based on current player with transparency
            if self.current_player == 1:
                preview_color = QColor(255, 0, 0)
            else:
                preview_color = QColor(255, 255, 0)

            qp.setBrush(QBrush(preview_color))
            qp.drawEllipse(highlight_x, self.offset_y - int(TILE_SIZE * 0.95), TILE_SIZE - SPACING, TILE_SIZE - SPACING)

        # Draw the holes and pieces
        for row in range(ROWS):
            for col in range(COLS):
                x = col * TILE_SIZE + self.offset_x
                y = row * TILE_SIZE + self.offset_y

                # Draw black holes
                qp.setBrush(QBrush(QColor(0, 0, 0)))  # Black holes
                qp.drawEllipse(x + int(SPACING / 2), int(y + SPACING / 2), TILE_SIZE - SPACING, TILE_SIZE - SPACING)

                # Draw pieces if they exist
                if self.board[row][col] == 1:
                    qp.setBrush(QBrush(QColor(255, 0, 0)))  # Red
                    qp.drawEllipse(x + int(SPACING / 2), int(y + SPACING / 2), TILE_SIZE - SPACING, TILE_SIZE - SPACING)
                elif self.board[row][col] == 2:
                    qp.setBrush(QBrush(QColor(255, 255, 0)))  # Yellow
                    qp.drawEllipse(x + int(SPACING / 2), int(y + SPACING / 2), TILE_SIZE - SPACING, TILE_SIZE - SPACING)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = ConnectFour()
    game.show()
    sys.exit(app.exec_())
