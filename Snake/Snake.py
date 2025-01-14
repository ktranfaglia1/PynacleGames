#  Author: Kyle Tranfaglia
#  Title: PynacleGames - Game02 - Snake
#  Last updated: 01/14/25
#  Description: This program uses PyQt5 packages to build the game 15-puzzle with an automatic solver using A* search
import sys
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QLabel


class SnakeGame(QGraphicsView):
    def __init__(self):
        super().__init__()

        # Game settings
        self.scene_width = 800
        self.scene_height = 800
        self.block_size = 20

        # Initialize the scene
        self.scene = QGraphicsScene(0, 0, self.scene_width, self.scene_height)
        self.setScene(self.scene)

        # Ensure the view fits the scene exactly and set window title and size
        self.setWindowTitle("Snake Game")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFixedSize(self.scene_width, self.scene_height)

        # Set up the snake and apple
        self.snake = []
        self.apple = None
        self.init_snake()
        self.spawn_apple()

        # Game mechanics
        self.direction = Qt.Key_Right
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(150)  # Update every 150 ms

        # Score label
        self.score = 0
        self.score_label = QLabel(f"Score: {self.score}", self)
        self.score_label.setStyleSheet("font-size: 16px; color: black;")
        self.score_label.move(10, 10)

        # Set up the game view
        self.setBackgroundBrush(QBrush(QColor("#010101")))  # Background color
        self.setFocusPolicy(Qt.StrongFocus)

    def init_snake(self):
        # Create the initial snake with 3 segments
        for i in range(3):
            segment = QGraphicsRectItem(self.block_size * (3 - i), 0, self.block_size, self.block_size)
            segment.setBrush(QBrush(QColor("green")))
            self.scene.addItem(segment)
            self.snake.append(segment)

    def spawn_apple(self):
        import random
        if self.apple:
            self.scene.removeItem(self.apple)

        x = random.randint(0, (self.scene_width // self.block_size) - 1) * self.block_size
        y = random.randint(0, (self.scene_height // self.block_size) - 1) * self.block_size

        self.apple = QGraphicsRectItem(x, y, self.block_size, self.block_size)
        self.apple.setBrush(QBrush(QColor("red")))
        self.scene.addItem(self.apple)

    def game_loop(self):
        # Get current head position
        head = self.snake[0]
        head_x = head.rect().x()
        head_y = head.rect().y()

        # Calculate new head position
        if self.direction == Qt.Key_Right:
            new_x = head_x + self.block_size
            new_y = head_y
        elif self.direction == Qt.Key_Left:
            new_x = head_x - self.block_size
            new_y = head_y
        elif self.direction == Qt.Key_Up:
            new_x = head_x
            new_y = head_y - self.block_size
        elif self.direction == Qt.Key_Down:
            new_x = head_x
            new_y = head_y + self.block_size

        # Check for collisions
        if self.is_collision(new_x, new_y):
            self.timer.stop()
            self.score_label.setText("Game Over!")
            return

        # Check if apple is eaten
        if self.apple and QRectF(new_x, new_y, self.block_size, self.block_size).intersects(self.apple.rect()):
            self.score += 10
            self.score_label.setText(f"Score: {self.score}")
            self.spawn_apple()
        else:
            tail = self.snake.pop()
            self.scene.removeItem(tail)

        # Add new head to the snake
        new_head = QGraphicsRectItem(new_x, new_y, self.block_size, self.block_size)
        new_head.setBrush(QBrush(QColor("green")))
        self.scene.addItem(new_head)
        self.snake.insert(0, new_head)

    def is_collision(self, x, y):
        # Check for wall collisions
        if x < 0 or x >= self.scene_width or y < 0 or y >= self.scene_height:
            return True

        # Check for self-collision
        for segment in self.snake:
            if segment.rect().x() == x and segment.rect().y() == y:
                return True

        return False

    def keyPressEvent(self, event):
        # Prevent the snake from reversing direction
        if event.key() == Qt.Key_Right and self.direction != Qt.Key_Left:
            self.direction = Qt.Key_Right
        elif event.key() == Qt.Key_Left and self.direction != Qt.Key_Right:
            self.direction = Qt.Key_Left
        elif event.key() == Qt.Key_Up and self.direction != Qt.Key_Down:
            self.direction = Qt.Key_Up
        elif event.key() == Qt.Key_Down and self.direction != Qt.Key_Up:
            self.direction = Qt.Key_Down


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = SnakeGame()
    game.show()
    sys.exit(app.exec_())
