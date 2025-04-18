#  Author: Kyle Tranfaglia
#  Title: PynacleGames - Game05 - Connect Four
#  Last updated: 04/03/25
#  Description: This program uses PyQt5 packages to build the game Connect Four with many AI bots of various strength
import sys
import random
import math
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QDialog, QVBoxLayout
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

# Constants for board size and appearance
ROWS = 6
COLS = 7
W_WIDTH = 1024
W_HEIGHT = 768
SPACING = 12
TILE_SIZE = 96


# Dialogue box to display AI difficulties
class DifficultyDialog(QDialog):
    difficulty_selected = pyqtSignal(str)  # Define a custom signal to pass the selected difficulty

    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Difficulty Menu")
        self.setFixedSize(400, 300)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)  # Remove '?' button
        self.setStyleSheet("background-color: #444444;")

        # Layout setup
        layout = QVBoxLayout(self)

        # Title label
        title = QLabel("Choose a Difficulty", self)
        title.setStyleSheet("color: white; font-size: 26px; font-weight: bold;")
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

        # Master button
        master_button = QPushButton("Master", self)
        master_button.setStyleSheet(
            "background-color: #673AB7; color: white; padding: 8px; border-radius: 10px; font-size: 20px;")
        master_button.setCursor(Qt.PointingHandCursor)
        master_button.clicked.connect(lambda: self.set_difficulty("Master"))
        layout.addWidget(master_button)

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
        self.offset_y = (W_HEIGHT - (TILE_SIZE * ROWS)) // 2 + 10

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
        self.result_label.setGeometry(312, 712, 400, 40)
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("""font-size: 36px; font-weight: bold; color: white;""")

        # Menu Button (Bottom Left)
        self.menu_button = QPushButton("Menu", self)
        self.menu_button.setGeometry(166, 706, 135, 50)
        self.menu_button.setStyleSheet("font-size: 20px; font-weight: bold; border-radius: 5px;"
                                       "background-color: gray; color: white;")
        self.menu_button.setCursor(Qt.PointingHandCursor)
        self.menu_button.clicked.connect(self.toggle_menu)

        # Restart Button (Bottom Right)
        self.restart_button = QPushButton("Restart", self)
        self.restart_button.setGeometry(W_WIDTH - 301, 706, 135, 50)
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
        title.setStyleSheet("color: white; font-size: 60px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)

        # Play game button
        play_button = QPushButton("Play", self)
        play_button.setStyleSheet("font-size: 30px; color: White; background-color: #E53935; padding: 24px;"
                                  "border-radius: 18px; width: 200px;")
        play_button.setCursor(Qt.PointingHandCursor)
        play_button.clicked.connect(self.toggle_menu)

        # Open difficulty dialogue box button
        difficulty_button = QPushButton("Select Difficulty", self)
        difficulty_button.setStyleSheet("font-size: 30px; color: White; background-color: #FFC107; padding: 24px;"
                                        "border-radius: 18px; width: 200px;")
        difficulty_button.setCursor(Qt.PointingHandCursor)
        difficulty_button.clicked.connect(self.select_difficulty)

        # Exit application button
        exit_button = QPushButton("Exit", self)
        exit_button.setStyleSheet("font-size: 30px; color: White; background-color: #455A64; padding: 24px;"
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

            # If AI's turn, trigger AI move after animation
            QTimer.singleShot(500, self.handle_ai_turn)

    # Animate pieces falling into place by quickly updating the board as the row increments
    def animate_piece(self):
        self.animation_current_row += 1
        self.update()

        # Check if animation has reached its target
        if self.animation_current_row >= self.animation_target_row:
            self.animation_timer.stop()
            self.animating = False
            self.board[self.animation_target_row][self.animation_col] = self.current_player

            # Hide hovering piece after move finishes
            self.selected_col = -1
            self.update()

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
        if self.win_flag == 0 and self.selected_col >= 0 and not self.animating:
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

    # Check for a win event
    def check_win(self, row, col):
        player = self.board[row][col]
        return self.check_win_for_position(row, col, player)

    # Check all positions to see if player has won
    def check_win_for_player(self, player):
        for row in range(ROWS):
            for col in range(COLS):
                if self.board[row][col] == player:
                    if self.check_win_for_position(row, col, player):
                        return True
        return False

    # Check if there's a win starting from a position
    def check_win_for_position(self, row, col, player):
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
        if new_col != self.selected_col and not self.animating:
            if self.difficulty != "Local" and self.current_player == 2:
                return
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

    # Have an AI play a move
    def ai_move(self):
        if self.difficulty == "Easy":
            self.ai_easy()
        elif self.difficulty == "Medium":
            self.ai_medium()
        elif self.difficulty == "Hard":
            self.ai_minimax()
        elif self.difficulty == "Master":
            self.ai_minimax()

    # Determine if an AI can play a move and initiate it
    def handle_ai_turn(self):
        if self.win_flag == 0 and self.difficulty != "Local" and self.current_player == 2:
            self.selected_col = -1  # Hide hovering piece while AI calculates
            self.update()  # Redraw to immediately remove the hover effect
            self.ai_move()

    # Play a random move
    def ai_easy(self):
        valid_columns = [col for col in range(COLS) if self.board[0][col] == 0]
        if valid_columns:
            col = random.choice(valid_columns)
            self.selected_col = col  # Show hovering piece above AI's selected column
            self.update()  # Redraw to reflect the change
            self.drop_piece(col)

    # Play a winning or blocking move if possible, otherwise play a random move
    def ai_medium(self):
        valid_columns = [col for col in range(COLS) if self.board[0][col] == 0]

        # Play winning move if possible
        for col in valid_columns:
            if self.simulate_move(col, self.current_player):
                self.selected_col = col  # Show hovering piece above AI's selected column
                self.update()  # Redraw to reflect the change
                self.drop_piece(col)
                return

        # Block opponent from winning
        opponent = 3 - self.current_player
        for col in valid_columns:
            if self.simulate_move(col, opponent):
                self.selected_col = col  # Show hovering piece above AI's selected column
                self.update()  # Redraw to reflect the change
                self.drop_piece(col)
                return

        # Play randomly otherwise
        col = random.choice(valid_columns)
        self.selected_col = col  # Show hovering piece above AI's selected column
        self.update()  # Redraw to reflect the change
        self.drop_piece(col)

    # Count the number of pieces on the board to determine move number
    def get_move_count(self):
        return sum(1 for row in self.board for cell in row if cell != 0)

    # Check if playing in this column creates a potential win in the next move
    def simulate_win_in_two(self, col, player):
        # Get the row where the piece would land
        for row in reversed(range(ROWS)):
            if self.board[row][col] == 0:
                # Place the piece
                self.board[row][col] = player

                # Check if this creates any immediate threats (position where placing a piece would create a win)
                threat_count = 0

                # Check all valid columns for potential win on next move
                for next_col in range(COLS):
                    if self.board[0][next_col] != 0:  # Column is full
                        continue

                    # Find row where next piece would go
                    next_row = -1
                    for r in reversed(range(ROWS)):
                        if self.board[r][next_col] == 0:
                            next_row = r
                            break

                    if next_row >= 0:
                        # Place the piece to check for win
                        self.board[next_row][next_col] = player

                        # Check if this is a win
                        if self.check_win_for_player(player):
                            threat_count += 1

                        # Remove the test piece
                        self.board[next_row][next_col] = 0

                # Remove the original piece
                self.board[row][col] = 0

                # If we found 2 or more threats, this is a winning move
                return threat_count >= 2

        return False

    # Main minimax function to find great moves for hard and master bot
    def ai_minimax(self):
        move_count = self.get_move_count()  # Get move count for early game optimizations
        center_col = COLS // 2

        # First AI move (second overall)
        if move_count == 1:
            self.selected_col = center_col
            self.update()
            self.drop_piece(center_col)
            return

        valid_columns = [col for col in range(COLS) if self.board[0][col] == 0]  # Get columns with empty tiles
        if not valid_columns:
            return

        # Play winning move if possible
        for col in valid_columns:
            if self.simulate_move(col, 2):  # AI can win
                self.selected_col = col
                self.update()
                self.drop_piece(col)
                return

        # Block opponent from winning
        for col in valid_columns:
            if self.simulate_move(col, 1):  # Block opponent
                self.selected_col = col
                self.update()
                self.drop_piece(col)
                return

        # Check for two-move win scenarios (unblockable forks)
        for col in valid_columns:
            if self.simulate_win_in_two(col, 2):  # AI can create a forced win
                self.selected_col = col
                self.update()
                self.drop_piece(col)
                return

        # Block opponent's two-move win scenarios
        for col in valid_columns:
            if self.simulate_win_in_two(col, 1):  # Block opponent's forced win
                self.selected_col = col
                self.update()
                self.drop_piece(col)
                return

        # Adjust search depth based on difficulty and game phase
        base_depth = 4 if self.difficulty == "Hard" else 6  # Base depth based on difficulty

        # Then adjust based on game phase
        if move_count <= 8:  # Early game
            current_depth = min(base_depth, 4)  # Cap at 4 for early game
        elif move_count <= 20:  # Mid-game
            current_depth = min(base_depth, 5)  # Cap at 5 for mid-game
        else:  # Late game
            current_depth = base_depth  # Use full depth for late game

        # Order columns differently based on game phase
        if move_count <= 8:
            # Early game: heavily favor center and adjacent columns
            ordered_columns = sorted(valid_columns,
                                     key=lambda x: (
                                         -15 * (x == center_col),  # Center highest priority
                                         -8 * (abs(x - center_col) == 1),  # Adjacent to center
                                         -3 * (abs(x - center_col) == 2),  # Two away from center
                                         abs(x - center_col)  # Others by distance
                                     ))
        else:
            # Mid-late game: more balanced approach
            ordered_columns = sorted(valid_columns,
                                     key=lambda x: (
                                         -8 * (x == center_col),  # Center still important
                                         -4 * (abs(x - center_col) == 1),  # Adjacent still good
                                         abs(x - center_col)  # Others by distance
                                     ))

        # Minimax search
        best_col = ordered_columns[0]  # Default to first column in prioritized list
        best_score = -math.inf
        memo = {}

        for col in ordered_columns:
            row = self.get_next_open_row(col)
            self.board[row][col] = 2  # AI's piece

            score = self.minimax_with_memo(current_depth, -math.inf, math.inf, False, memo)

            self.board[row][col] = 0

            if score > best_score:
                best_score = score
                best_col = col

        self.selected_col = best_col
        self.update()
        self.drop_piece(best_col)

    # Minimax algorithm with memoization to prevent redundant calculations
    def minimax_with_memo(self, depth, alpha, beta, maximizing, memo):
        # Terminal state checks
        if self.check_win_for_player(2):
            return 100000
        if self.check_win_for_player(1):
            return -100000
        if all(self.board[0][col] != 0 for col in range(COLS)):
            return 0

        if depth == 0:
            return self.evaluate_board()

        # Only create hash for memoization if needed
        memo_key = None
        if depth <= 2:
            # Lighter board hashing using Zobrist-inspired approach
            board_hash = 0
            for r in range(ROWS):
                for c in range(COLS):
                    if self.board[r][c] != 0:
                        # Use a simpler hashing scheme: position * 3 + piece
                        index = r * COLS + c
                        piece_val = self.board[r][c]
                        board_hash ^= (index * 3 + piece_val) * 73  # Prime multiplier helps distribution

            memo_key = (board_hash, depth, maximizing)

            # Return cached result if available
            if memo_key in memo:
                return memo[memo_key]

        valid_columns = [col for col in range(COLS) if self.board[0][col] == 0]

        # Order columns by distance from center for better pruning
        center_col = COLS // 2
        valid_columns.sort(key=lambda x: abs(x - center_col))

        if maximizing:  # AI's turn
            value = -math.inf
            for col in valid_columns:
                row = self.get_next_open_row(col)
                if row == -1:  # Skip full columns
                    continue

                self.board[row][col] = 2
                new_score = self.minimax_with_memo(depth - 1, alpha, beta, False, memo)
                self.board[row][col] = 0
                value = max(value, new_score)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break

            # Store result for shallow depths
            if depth <= 2 and memo_key is not None:
                memo[memo_key] = value

            return value

        else:  # Human's turn
            value = math.inf
            for col in valid_columns:
                row = self.get_next_open_row(col)
                if row == -1:  # Skip full columns
                    continue

                self.board[row][col] = 1
                new_score = self.minimax_with_memo(depth - 1, alpha, beta, True, memo)
                self.board[row][col] = 0
                value = min(value, new_score)
                beta = min(beta, value)
                if alpha >= beta:
                    break

            # Store result for shallow depths
            if depth <= 2 and memo_key is not None:
                memo[memo_key] = value

            return value

    # Check if the current board state is terminal (win or draw)
    def check_for_terminal(self):
        # Check for wins
        if self.check_win_for_player(1) or self.check_win_for_player(2):
            return True

        # Check for draw (board is full)
        if all(self.board[0][col] != 0 for col in range(COLS)):
            return True

        return False

    # Get the next open row
    def get_next_open_row(self, col):
        for row in reversed(range(ROWS)):
            if self.board[row][col] == 0:
                return row
        return -1  # Shouldn't happen

    # Evaluate a board state
    def evaluate_board(self):
        score = 0

        # Center column preference
        center_col = COLS // 2
        center_array = [self.board[row][center_col] for row in range(ROWS)]
        center_ai_count = center_array.count(2)
        score += center_ai_count * 6  # Higher weight for center control

        # Evaluate all possible windows of 4

        # Horizontal windows
        for row in range(ROWS):
            for col in range(COLS - 3):
                window = [self.board[row][col + i] for i in range(4)]
                score += self.score_window(window)

        # Vertical windows
        for col in range(COLS):
            for row in range(ROWS - 3):
                window = [self.board[row + i][col] for i in range(4)]
                score += self.score_window(window)

        # Positive diagonal windows
        for row in range(ROWS - 3):
            for col in range(COLS - 3):
                window = [self.board[row + i][col + i] for i in range(4)]
                score += self.score_window(window)

        # Negative diagonal windows
        for row in range(3, ROWS):
            for col in range(COLS - 3):
                window = [self.board[row - i][col + i] for i in range(4)]
                score += self.score_window(window)

        # Bonus for controlling lower rows (foundation pieces)
        for col in range(COLS):
            for row in range(ROWS - 2, ROWS):  # Bottom two rows
                if self.board[row][col] == 2:
                    score += 2  # Small bonus for lower positions

        return score

    # Get a score for a window (game board subset) to favor AI piece clustering and stray from human piece clustering
    def score_window(self, window):
        ai_count = window.count(2)
        human_count = window.count(1)
        empty_count = window.count(0)

        # Base scoring
        if ai_count == 4:
            return 1000000  # Certain win
        elif ai_count == 3 and empty_count == 1:
            return 100  # Strong threat
        elif ai_count == 2 and empty_count == 2:
            return 10  # Developing position

        if human_count == 4:
            return -1000000  # Certain loss
        elif human_count == 3 and empty_count == 1:
            return -100  # Urgent threat
        elif human_count == 2 and empty_count == 2:
            return -10  # Potential threat

        return 0

    # Helper function to simulate a move and check if it leads to a win
    def simulate_move(self, col, player):
        for row in reversed(range(ROWS)):
            if self.board[row][col] == 0:
                self.board[row][col] = player
                win = self.check_win(row, col)
                self.board[row][col] = 0
                return win
        return False

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
