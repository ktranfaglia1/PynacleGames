#  Author: Kyle Tranfaglia
#  Title: PynacleGames - Game02 - Snake
#  Last updated: 02/05/25
#  Description: This program uses PyQt5 packages to build the game Snake with some unique features
import sys
import os
import random
from datetime import datetime
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
                             QLabel, QPushButton, QDialog, QVBoxLayout)


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
        title = QLabel("Top 10 High Scores")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: Blue; text-decoration: underline;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Display the scores
        for i, (score, timestamp) in enumerate(scores, start=1):
            score_label = QLabel(f"{i}. {score} -- {timestamp}")
            score_label.setStyleSheet("font-size: 22px; color: black;")
            score_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(score_label)

        # Add an exit button
        exit_button = QPushButton("Close")
        exit_button.setStyleSheet("font-size: 18px; color: White; background-color: Red; padding: 9px;")
        exit_button.clicked.connect(self.close)
        exit_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(exit_button, alignment=Qt.AlignLeft)

        self.setLayout(layout)


# Apple object that can be one of four types
class Apple(QGraphicsRectItem):
    def __init__(self, x, y, size, apple_type):
        super().__init__(x, y, size, size)
        self.apple_type = apple_type  # Set apple type given parameter

        # Color the apple object given the apple type
        if apple_type == "Green":
            self.setBrush(QBrush(QColor("Lime")))
        elif apple_type == "Silver":
            self.setBrush(QBrush(QColor("Silver")))
        elif apple_type == "Gold":
            self.setBrush(QBrush(QColor("Gold")))
        else:
            self.setBrush(QBrush(QColor("Purple")))


# Main application for Snake Game
class SnakeGame(QGraphicsView):
    def __init__(self):
        super().__init__()

        # Game settings
        self.scene_width = 800
        self.scene_height = 800
        self.block_size = 32
        self.max_blocks = (self.scene_height // self.block_size) - 1

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

        # Game loop timer
        self.delay = 200  # Update every 200 ms
        self.delay_decrement = 8  # Delay change per apples eaten
        self.min_delay = 80
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(self.delay)

        # Score label
        self.score = 0
        self.score_label = QLabel(f"Score: {self.score}", self)
        self.score_label.setStyleSheet("font-type: Arial; font-size: 24px; color: white;")
        self.score_label.move(10, 10)
        self.score_label.setFixedWidth(200)

        # Set up the game view
        self.setBackgroundBrush(QBrush(QColor("#010101")))
        self.setFocusPolicy(Qt.StrongFocus)

        # Game mechanics
        self.direction = Qt.Key_Right
        self.overlay_items = []

    # Create the initial snake with 3 segments
    def init_snake(self):
        for i in range(3):
            segment = QGraphicsRectItem(self.block_size * (3 - i), 0, self.block_size, self.block_size)
            segment.setBrush(QBrush(QColor("Violet")))
            self.scene.addItem(segment)
            self.snake.append(segment)

    # Spawn in an apple object
    def spawn_apple(self):
        # Remove current apple if exists
        if self.apple:
            self.scene.removeItem(self.apple)

        # Generate random coordinates for apple spawn location until valid
        while True:
            x = random.randint(0, (self.scene_width // self.block_size) - 1) * self.block_size
            y = random.randint(0, (self.scene_height // self.block_size) - 1) * self.block_size

            # Check if the apple would spawn inside the snake
            if not self.is_collision(x, y):
                break  # Found a valid position

        z = random.randint(0, 99)  # Get random number (0-99) for apple type

        # Set an apple type given the random z value
        if z > 30:
            apple_type = "Green"
        elif z >= 13:
            apple_type = "Silver"
        elif z >= 4:
            apple_type = "Gold"
        else:
            apple_type = "Poison"

        # Create the apple and add it to the scene
        self.apple = Apple(x, y, self.block_size, apple_type)
        self.scene.addItem(self.apple)

    # Main game loop
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
        else:
            new_x, new_y = head_x, head_y

        # Check for collisions
        if self.is_collision(new_x, new_y):
            self.timer.stop()
            self.draw_overlay()  # Signifies game end
            return

        # Check if apple is eaten
        if self.apple and QRectF(new_x, new_y, self.block_size, self.block_size).intersects(self.apple.rect()):
            # Check apple type and increase score accordingly
            if self.apple.apple_type == "Green":
                self.score += 10
            elif self.apple.apple_type == "Silver":
                self.score += 25
            elif self.apple.apple_type == "Gold":
                self.score += 50
            else:  # No points added but removes half of snake body
                for i in range((len(self.snake) // 2) + 1):
                    tail = self.snake.pop()
                    self.scene.removeItem(tail)

            # Update the delay (decrement)
            self.delay = max(self.min_delay, self.delay - self.delay_decrement)
            self.timer.setInterval(self.delay)

            # Update the score label and spawn a new apple
            self.score_label.setText(f"Score: {self.score}")
            self.score_label.adjustSize()
            self.spawn_apple()
        else:  # Apple not eaten, continue moving snake
            tail = self.snake.pop()
            self.scene.removeItem(tail)

        # Add new head to the snake (next tile in current direction)
        new_head = QGraphicsRectItem(new_x, new_y, self.block_size, self.block_size)
        new_head.setBrush(QBrush(QColor("Violet")))
        self.scene.addItem(new_head)
        self.snake.insert(0, new_head)

    # Check for all possible collisions
    def is_collision(self, x, y):
        # Check for wall collisions
        if x < 0 or x >= self.scene_width or y < 0 or y >= self.scene_height:
            return True

        # Check for self-collision
        for segment in self.snake:
            if segment.rect().x() == x and segment.rect().y() == y:
                return True

        return False

    # Handle key press for snake movement
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

    # Draw the Game Over overlay
    def draw_overlay(self):
        self.save_score()  # Save the current score

        # Semi-transparent background
        overlay = QGraphicsRectItem(0, 0, self.scene_width, self.scene_height)
        overlay.setBrush(QBrush(QColor(0, 0, 0, 150)))
        self.scene.addItem(overlay)

        # Game Over text
        game_over_text = self.scene.addText("Game Over")
        game_over_text.setDefaultTextColor(QColor("white"))
        game_over_text.setScale(4)
        text_rect = game_over_text.boundingRect()
        game_over_text.setPos(
            (self.scene_width - text_rect.width() * 4) / 2, self.scene_height / 2 - 180)

        # Play Again button
        play_again_button = QPushButton("Play Again", self)
        play_again_button.setStyleSheet("font-size: 24px; color: White; background-color: Green; padding: 12px;")
        play_again_button.resize(180, 60)
        play_again_button.move((self.scene_width - 180) // 2, self.scene_height // 2 - 72)
        play_again_button.show()
        play_again_button.setCursor(Qt.PointingHandCursor)
        play_again_button.clicked.connect(self.restart_game)

        # High Scores button
        high_scores_button = QPushButton("High Scores", self)
        high_scores_button.setStyleSheet("font-size: 24px; color: White; background-color: Blue; padding: 12px;")
        high_scores_button.resize(180, 60)
        high_scores_button.move((self.scene_width - 180) // 2, self.scene_height // 2)
        high_scores_button.show()
        high_scores_button.setCursor(Qt.PointingHandCursor)
        high_scores_button.clicked.connect(self.display_high_scores)

        # Exit button
        exit_button = QPushButton("Exit", self)
        exit_button.setStyleSheet("font-size: 24px; color: White; background-color: Red; padding: 12px;")
        exit_button.resize(180, 60)
        exit_button.move((self.scene_width - 180) // 2, self.scene_height // 2 + 72)
        exit_button.show()
        exit_button.setCursor(Qt.PointingHandCursor)
        exit_button.clicked.connect(self.close)

        # Keep references to avoid garbage collection
        self.overlay_items = [overlay, game_over_text, play_again_button, exit_button, high_scores_button]

    # Restart the game
    def restart_game(self):
        # Clear the scene
        for item in self.overlay_items:
            if isinstance(item, QPushButton):
                item.deleteLater()
            else:
                self.scene.removeItem(item)
        self.overlay_items.clear()  # Remove all item references in list

        # Reset game state to default (start)
        self.scene.clear()
        self.snake.clear()
        self.score = 0
        self.score_label.setText(f"Score: {self.score}")
        self.score_label.adjustSize()
        self.snake = []
        self.apple = None
        self.init_snake()
        self.spawn_apple()
        self.direction = Qt.Key_Right
        self.delay = 200
        self.timer.start(self.delay)

    # Save score and date/time in a txt file
    def save_score(self):
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d -- %H:%M:%S")
        with open("scores.txt", "a") as file:
            file.write(f"{self.score},{formatted_time}\n")

    # Load all scores and dates/times for score txt file and return a sorted list (descending)
    def load_scores(self):
        if not os.path.exists("scores.txt"):
            return []
        with open("scores.txt", "r") as file:
            scores = []
            # Parse the txt file to gather scores and dates/times
            for line in file:
                parts = line.strip().split(",")
                if len(parts) == 2 and parts[0].isdigit():
                    score = int(parts[0])
                    timestamp = parts[1]
                    scores.append((score, timestamp))
        return sorted(scores, key=lambda x: x[0], reverse=True)  # Return sorted list (descending) by score

    # Create the high scores dialog box and display the top ten high scores
    def display_high_scores(self):
        scores = self.load_scores()
        top_scores = scores[:10]
        dialog = HighScoresDialog(self, top_scores)
        dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = SnakeGame()
    game.show()
    sys.exit(app.exec_())
