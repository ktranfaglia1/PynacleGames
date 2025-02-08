#  Author: Kyle Tranfaglia
#  Title: PynacleGames - Game04 - 2048
#  Last updated:  02/07/25
#  Description: This program uses PyQt5 packages to build the game 2048
import sys
import random
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QFont, QColor, QPainterPath, QBrush, QPen
from PyQt5.QtCore import Qt, QRect

CELL_COUNT = 4
CELL_SIZE = 150
CELL_PADDING = 12
CORNER_RADIUS = 16
W_WIDTH = 800
W_HEIGHT = 800

# Calculate grid width and height
grid_width = CELL_COUNT * (CELL_SIZE + CELL_PADDING) - CELL_PADDING
grid_height = CELL_COUNT * (CELL_SIZE + CELL_PADDING) - CELL_PADDING

# Calculate centered origin
GRID_ORIGINX = (W_WIDTH - grid_width) // 2
GRID_ORIGINY = (W_HEIGHT - grid_height) // 2

text_color = QColor(255, 255, 255)
border_color = QColor(30, 30, 30)

# Define color scheme for dark theme
tile_colors = {
    0: QColor(50, 50, 50),
    2: QColor(89, 89, 89),
    4: QColor(102, 102, 102),
    8: QColor(153, 76, 0),
    16: QColor(204, 102, 0),
    32: QColor(255, 128, 0),
    64: QColor(255, 102, 0),
    128: QColor(204, 204, 0),
    256: QColor(153, 204, 0),
    512: QColor(102, 204, 0),
    1024: QColor(51, 204, 0),
    2048: QColor(0, 204, 102),
}


class TwentyFortyEight(QWidget):
    def __init__(self):
        super().__init__()
        self.__moves = 0
        self.points = 0
        self.__board = [[0 for _ in range(CELL_COUNT)] for _ in range(CELL_COUNT)]
        self.initUI()
        self.add_random_tile()
        self.add_random_tile()
        self.show()

    def initUI(self):
        self.setWindowTitle('2048')
        self.setFixedSize(W_WIDTH, W_HEIGHT)
        self.setStyleSheet("background-color: #010101;")

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
                        qp.setPen(text_color)
                        qp.setFont(QFont('Arial', 30, QFont.Bold))
                        text = str(value)
                        text_width = qp.fontMetrics().width(text)
                        text_height = qp.fontMetrics().height()
                        qp.drawText((x + (CELL_SIZE - text_width) // 2),
                                    (y + (CELL_SIZE + text_height - CELL_PADDING) // 2), text)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
            print(f"Key pressed: {event.key()}")  # Debugging step
            self.move_tiles(event.key())
            self.add_random_tile()
            self.update()

    def move_tiles(self, direction):
        print(f"Moving {direction}")  # Debugging step

        def slide(row):
            new_row = [value for value in row if value != 0]
            i = 0
            while i < len(new_row) - 1:
                if new_row[i] == new_row[i + 1]:
                    new_row[i] *= 2
                    self.points += new_row[i]
                    del new_row[i + 1]
                    new_row.append(0)  # Maintain length
                i += 1
            return new_row + [0] * (CELL_COUNT - len(new_row))

        original_board = [row[:] for row in self.__board]  # Copy for comparison
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

        # Check if move changed the board before adding a new tile
        if self.__board != original_board:
            self.add_random_tile()

    def add_random_tile(self):
        empty_cells = [(r, c) for r in range(CELL_COUNT) for c in range(CELL_COUNT) if self.__board[r][c] == 0]
        if empty_cells:
            r, c = random.choice(empty_cells)
            self.__board[r][c] = 2 if random.random() < 0.9 else 4
            print(f"Added tile {self.__board[r][c]} at ({r}, {c})")  # Debugging step


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = TwentyFortyEight()
    sys.exit(app.exec_())

