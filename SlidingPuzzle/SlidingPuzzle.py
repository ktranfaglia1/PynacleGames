#  Author: Kyle Tranfaglia
#  Title: PynacleGames - Game01 - SlidingPuzzle (15-Puzzle)
#  Last updated: 03/06/25
#  Description: This program uses PyQt5 packages to build the game 15-puzzle with an automatic solver using A* search
import sys
import random
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QGuiApplication
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton
from PyQt5.QtCore import Qt, QTimer
import heapq

# Set game specifications: window size, cell/grid size, cell count, and grid starting location
CELL_COUNT = 4
CELL_SIZE = 160
W_WIDTH = 1024
W_HEIGHT = 768
GRID_ORIGINX = (W_WIDTH - (CELL_SIZE * CELL_COUNT)) // 2
GRID_ORIGINY = 60

# Goal state as tuple (flat | 1D)
GOAL_STATE = tuple(range(1, 16)) + (0,)

# Goal state as dictionary to represent a value with its goal coordinates (r,c)
GOAL_POSITIONS = {val: (i // 4, i % 4) for i, val in enumerate(GOAL_STATE)}


# Calculate the manhattan distance to get a heuristic cost for from the current board state to the solved state
def manhattan_heuristic(board):
    distance = 0
    # Iterate over each tile in the board with its index
    for index, tile in enumerate(board):
        # Get the goal row and column for the current tile from the predefined goal positions
        goal_row, goal_col = GOAL_POSITIONS[tile]

        # Calculate the current row and column of the tile in the board
        row, col = index // 4, index % 4

        # Update the heuristic value by summing the absolute differences in the rows and columns for each tile
        distance += abs(goal_row - row) + abs(goal_col - col)
    return distance * 1.75  # Scale the heuristic for improved guidance


# A* Search to find the optimal path solution to the puzzle
def a_star_search(start_state):
    # Define all possible tile swaps (as indexes) for each index (up, down, left, right)
    moves = {
        0: [1, 4], 1: [0, 2, 5], 2: [1, 3, 6], 3: [2, 7],
        4: [0, 5, 8], 5: [1, 4, 6, 9], 6: [2, 5, 7, 10], 7: [3, 6, 11],
        8: [4, 9, 12], 9: [5, 8, 10, 13], 10: [6, 9, 11, 14], 11: [7, 10, 15],
        12: [8, 13], 13: [9, 12, 14], 14: [10, 13, 15], 15: [11, 14]
    }
    # Convert the start state (2D list) into a tuple for hashing and make a list to act as the priority queue
    start_state = tuple(start_state[i][j] for i in range(4) for j in range(4))
    exploration_queue = []

    empty_index = start_state.index(0)  # Find the index of the empty tile (represented by 0) in the start state

    # Push the initial state into the list (f, g, h, state, empty index, path)
    heapq.heappush(exploration_queue, (0, 0, manhattan_heuristic(start_state), start_state, empty_index, []))

    # Dictionary to store visited states and their true path costs
    visited = {start_state: 0}

    # A* loop to iterate until there are no states left to explore (no solution)
    while exploration_queue:
        # Pop the state with the lowest f value from the list (f and h not needed)
        _, g, _, current_state, empty_index, path = heapq.heappop(exploration_queue)

        # Check if the current state is the goal state
        if current_state == GOAL_STATE:
            return path  # Return the path of moves to reach the goal state (list of 1D indexes)

        # Explore all possible moves from the current state, determined by the empty tile's position
        for move in moves[empty_index]:
            # Create a new state by swapping the empty tile with a neighboring tile
            new_state = list(current_state)
            new_state[empty_index], new_state[move] = new_state[move], new_state[empty_index]
            new_state = tuple(new_state)

            # Calculate the costs for the new state
            new_g = g + 1  # g increments for each move
            h = manhattan_heuristic(new_state)  # Calculate the heuristic: total manhattan distance of state
            f = new_g + h  # Compute the total cost by summing true cost and estimated cost

            # Cycle Detection: check if the state has been visited with a lower or equal g value
            if new_state not in visited or new_g < visited[new_state]:
                visited[new_state] = new_g  # Update the visited dictionary with the new state's g value
                heapq.heappush(exploration_queue, (f, new_g, h, new_state, move, path + [move]))

    return None  # Return None to indicate failure


# Sliding puzzle object to handle all game setup and functionality
class SlidingPuzzle(QWidget):

    def __init__(self):
        super().__init__()

        # Set game defaults
        self.__moves = 0
        self.win = False
        self.__board = [[-1 for _ in range(CELL_COUNT)] for _ in range(CELL_COUNT)]
        self.__order = None
        self.setMouseTracking(True)
        self.initUI()
        self.initialize_board()

        # Setup timer and variables for solving the puzzle
        self.solving = False
        self.solution_path = None
        self.solution_index = 0
        self.solution_timer = QTimer(self)

        # Setup timer to display seconds and milliseconds since the puzzle was started
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.elapsed_time = 0
        self.timer.start(100)  # Update every millisecond second

        # Create a reset button outside the grid (top-right corner)
        self.reset_button = QPushButton('Reset', self)
        self.reset_button.setStyleSheet("""QPushButton {background-color: #cc6666; border: 1px solid black; 
        border-radius: 5px; font-size: 19px; font-type: Arial;}""")
        self.reset_button.setGeometry(W_WIDTH - 268, GRID_ORIGINY - 46, 78, 39)
        self.reset_button.setCursor(Qt.PointingHandCursor)
        self.reset_button.clicked.connect(self.play_again)

        # Create a solve button outside the grid
        self.solve_button = QPushButton('Solve', self)
        self.solve_button.setStyleSheet("""QPushButton {background-color: #66cc66; border: 1px solid black; 
        border-radius: 5px; font-size: 19px; font-type: Arial;}""")
        self.solve_button.setGeometry(W_WIDTH - 354, GRID_ORIGINY - 46, 78, 39)
        self.solve_button.setCursor(Qt.PointingHandCursor)
        self.solve_button.clicked.connect(self.display_solution)

        self.show()

    def initUI(self):
        # Set window title and size
        self.setWindowTitle('SlidingPuzzle')
        self.setFixedSize(W_WIDTH, W_HEIGHT)
        self.setStyleSheet("background-color: #010101;")

        # Center the window on the screen
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    # Initializes the board with random cell numbers if solvable
    def initialize_board(self):
        # Initialize and shuffle the cell order array
        self.__order = list(range(CELL_COUNT * CELL_COUNT))
        random.shuffle(self.__order)  # Initial shuffle

        # Shuffle the board order until the permutation is solvable
        while not self.is_solvable():
            random.shuffle(self.__order)

        # Populate the board with the shuffled numbers by row
        index = 0
        for r in range(CELL_COUNT):
            for c in range(CELL_COUNT):
                self.__board[r][c] = self.__order[index]
                index += 1

    # Check if the current board shuffle is solvable using a mathematical formula that counts inversions
    def is_solvable(self):
        inversions = self.count_inversions()  # Get number of inversions
        empty_row = CELL_COUNT - (self.__order.index(0) // CELL_COUNT)  # Find row from bottom with empty cell

        # Check grid width (compatible with future cell amount changes) and assess inversions rule
        if CELL_COUNT % 2 == 1:  # Odd Width
            return inversions % 2 == 0
        else:  # Even Width
            if empty_row % 2 == 1:  # Empty space on an odd row (counting from the bottom)
                return inversions % 2 == 0
            else:  # Empty space on an even row
                return inversions % 2 == 1

    # Count the number of inversions on the board (when a cell precedes another cell with a smaller number on it)
    def count_inversions(self):
        inversions = 0
        # Loop through 1D ordered board and counting inversions (ignore empty cell)
        for i in range(len(self.__order)):
            for j in range(i + 1, len(self.__order)):
                if self.__order[i] != 0 and self.__order[j] != 0 and self.__order[i] > self.__order[j]:
                    inversions += 1
        return inversions

    # Creates and updates game grid
    def paintEvent(self, event):
        # Setup QPainter
        qp = QPainter()
        qp.begin(self)
        qp.setFont(QFont('Arial', 18))

        # Fill the entire grid region with light grey color
        grid_width = grid_height = CELL_COUNT * CELL_SIZE
        qp.fillRect(GRID_ORIGINX, GRID_ORIGINY, grid_width, grid_height, QColor(100, 100, 100))

        # if self.solving:
        #     qp.setPen(QPen(QColor(220, 0, 0)))
        #     qp.drawText(GRID_ORIGINX + 20, GRID_ORIGINY - 60, "PLEASE WAIT - SOLUTION IN PROGRESS")

        # Set text font and color, then draw the move counter above the top-left corner of the grid
        qp.setPen(QPen(QColor(60, 120, 255)))
        qp.drawText(GRID_ORIGINX, GRID_ORIGINY - 15, f"Moves: {self.__moves}")

        # Convert milliseconds to seconds and milliseconds
        seconds = self.elapsed_time // 1000
        milliseconds = (self.elapsed_time % 1000) // 100

        # Draw the timer above the grid
        qp.setPen(QPen(QColor(232, 232, 232)))
        qp.drawText(GRID_ORIGINX + 180, GRID_ORIGINY - 15, f"Time: {seconds}.{milliseconds} seconds")

        # Draw the instructional text below the board
        qp.drawText(GRID_ORIGINX + 72, GRID_ORIGINY + grid_height + 42, "Order the cells chronologically to win!")

        qp.setFont(QFont('Montserrat Bold', 20, QFont.Bold))

        # Loop through 2D board array and draw the board with numerically labeled cells
        for r in range(len(self.__board)):
            for c in range(len(self.__board[r])):
                number = self.__board[r][c]  # Get the number at the current position

                # Draw the number if it's not 0 (0 represents the empty tile)
                if number != 0:
                    # Calculate cell center (x,y)
                    text_x = GRID_ORIGINX + c * CELL_SIZE + CELL_SIZE // 2 - 12  # Center horizontally
                    text_y = GRID_ORIGINY + r * CELL_SIZE + CELL_SIZE // 2 + 12  # Center vertically

                    # Adjust x coordinate to center for double-digit numbers
                    if number / 10 >= 1:
                        text_x -= 10  # Shift text to the left for double digits

                    qp.drawText(text_x, text_y, str(number))  # Draw the number centered in the cell
                else:
                    # Fill the empty block
                    qp.fillRect(GRID_ORIGINX + c * CELL_SIZE + 2, GRID_ORIGINY + r * CELL_SIZE + 2,
                                CELL_SIZE - 1, CELL_SIZE - 1, QColor(138, 43, 226))

                # Draw the cell border
                qp.drawRect(GRID_ORIGINX + c * CELL_SIZE, GRID_ORIGINY + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                qp.drawRect(GRID_ORIGINX + c * CELL_SIZE - 1, GRID_ORIGINY + r * CELL_SIZE - 1,
                            CELL_SIZE + 2, CELL_SIZE + 2)

        # Check if the user won
        if self.win:
            self.timer.stop()
            self.draw_overlay(qp, seconds, milliseconds)  # Show the victory overlay
        qp.end()

    # Change cursor to pointing hand when hovering over a movable tile
    def mouseMoveEvent(self, event):
        # Get grid location of the mouse
        row = (event.y() - GRID_ORIGINY) // CELL_SIZE
        col = (event.x() - GRID_ORIGINX) // CELL_SIZE

        # Ensure the position is within the valid grid range
        if 0 <= row < CELL_COUNT and 0 <= col < CELL_COUNT:
            empty_row, empty_col = self.find_empty_cell()

            # Check if the hovered tile is adjacent to the empty tile
            if row == empty_row or col == empty_col:
                self.setCursor(Qt.PointingHandCursor)  # Change cursor to pointing hand
            else:
                self.setCursor(Qt.ArrowCursor)  # Revert to default cursor
        else:
            self.setCursor(Qt.ArrowCursor)  # Revert if outside the grid

    # Handle mouse click event
    def mousePressEvent(self, event):
        # Check for active solution animation
        if self.solving:
            return  # Ignore clicks

        # Check for user win
        if self.win:
            self.play_again()  # Reset the game
            return

        # Calculate row and column of mouse click
        row = (event.y() - GRID_ORIGINY) // CELL_SIZE
        col = (event.x() - GRID_ORIGINX) // CELL_SIZE

        # Check that the row and column are within the CELL_COUNT * CELL_COUNT grid
        if 0 <= row < CELL_COUNT and 0 <= col < CELL_COUNT:
            empty_row, empty_col = self.find_empty_cell()  # Find the position of the empty cell (denoted by 0)

            # Check if cell is in the same row as the empty cell
            if row == empty_row:
                move_count = abs(col - empty_col)  # Number of cells to move
                if col < empty_col:  # Slide right
                    for i in range(empty_col, col, -1):
                        self.__board[row][i] = self.__board[row][i - 1]
                elif col > empty_col:  # Slide left
                    for i in range(empty_col, col):
                        self.__board[row][i] = self.__board[row][i + 1]

            # Check if cell is in the same column as the empty cell
            elif col == empty_col:
                move_count = abs(row - empty_row)  # Number of cells to move
                if row < empty_row:  # Slide down
                    for i in range(empty_row, row, -1):
                        self.__board[i][col] = self.__board[i - 1][col]
                elif row > empty_row:  # Slide up
                    for i in range(empty_row, row):
                        self.__board[i][col] = self.__board[i + 1][col]

            # Clicked cell is not swappable
            else:
                return

            self.__board[row][col] = 0  # place empty cell at the clicked position
            self.__moves += move_count  # Update move count by the number of cells that moved
            self.check_win()  # Check if user won
            self.update()

    # Return location (row, column) of the empty cell
    def find_empty_cell(self):
        # Find the row and column of the empty cell (denoted by 0)
        for r in range(CELL_COUNT):
            for c in range(CELL_COUNT):
                if self.__board[r][c] == 0:
                    return r, c

    # Draw the victory screen to let the user know they won
    def draw_overlay(self, qp, seconds, milliseconds):
        qp.fillRect(self.rect(), QColor(128, 128, 128))  # Draw the grey overlay

        # Display win message
        qp.setPen(QPen(Qt.white))
        qp.setFont(QFont('Arial', 28))
        qp.drawText(self.rect(), Qt.AlignCenter, f"CONGRATULATIONS \n\n You solved the puzzle in"
                                                 f" {seconds} seconds \n using {self.__moves} moves!"
                                                 f" \n\n Click anywhere to play again.")

    # Check if the user won the game (all 15 numbered cells are in order)
    def check_win(self):
        # Check if the board is in the solved state
        flattened_board = [cell for row in self.__board for cell in row]  # Flatten board for list comparison

        # Check if the ordered list matches the flattened board
        if flattened_board == list(range(1, CELL_COUNT * CELL_COUNT)) + [0]:
            self.win = True
            self.reset_button.hide()  # Hide the reset button in victory overlay
            self.solve_button.hide()  # Hide the solve button in victory overlay
            self.update()

    # Reset the game, as in, set a new random state on board and set moves to 0
    def play_again(self):
        # Reset the game state
        self.__board = [[-1 for _ in range(CELL_COUNT)] for _ in range(CELL_COUNT)]
        self.__order = None
        self.__moves = 0
        self.win = False
        self.solution_path = []
        self.solution_index = 0
        self.initialize_board()
        self.reset_button.show()  # Reveal the reset button
        self.solve_button.show()  # Reveal the solve button
        self.elapsed_time = 0  # Reset the elapsed time
        self.timer.start()  # Restart the timer
        self.update()

    # Update the timer
    def update_time(self):
        self.elapsed_time += 100  # Increment the elapsed time by 1 millisecond
        self.update()  # Trigger a repaint to show the updated time

    # Use A* Search to find a path to the goal state and display it by moving the tiles every .5-seconds
    def display_solution(self):
        self.solving = True  # Set the solving in progress flag
        self.solve_button.setEnabled(False)  # Disable Solve button
        self.reset_button.setEnabled(False)  # Disable Reset button
        self.repaint()  # Immediately update the display to disable clicks

        self.solution_path = a_star_search(self.__board)  # Store the solution path

        # Safely disconnect any existing connections
        try:
            self.solution_timer.timeout.disconnect(self.solution_step)
        except TypeError:
            pass  # No previous connection, ignore the error and continue
        self.solution_timer.timeout.connect(self.solution_step)  # Connect to the step (utility) function
        self.solution_timer.start(600)  # 0.6-second delay for each move

    # Utility function to animate the solution by converting the 1D index to a 2D position and swapping the cells
    def solution_step(self):
        # Continue until goal state is reached (end of solution path)
        if self.solution_index < len(self.solution_path):
            swap_index = self.solution_path[self.solution_index]  # Get 1D index to swap with empty cell
            swap_pos = (swap_index // CELL_COUNT, swap_index % CELL_COUNT)  # Convert to 2D index (row, col)

            empty_pos = self.find_empty_cell()  # Get the current position of the empty cell

            # Perform the swap between the empty cell and the specified tile
            self.__board[empty_pos[0]][empty_pos[1]], self.__board[swap_pos[0]][swap_pos[1]] = \
                self.__board[swap_pos[0]][swap_pos[1]], self.__board[empty_pos[0]][empty_pos[1]]

            self.__moves += 1  # Increment the move counter
            self.solution_index += 1  # Move to the next step in the solution path
            self.update()  # Update the display
        else:
            self.solving = False
            self.solution_timer.stop()  # Stop the timer when the solution is complete
            self.solve_button.setEnabled(True)  # Enable Solve button
            self.reset_button.setEnabled(True)  # Enable Reset button
            self.check_win()  # Check for a win condition (goal state met)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SlidingPuzzle()
    sys.exit(app.exec_())
