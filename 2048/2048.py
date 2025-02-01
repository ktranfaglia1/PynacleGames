#  Author: Kyle Tranfaglia
#  Title: PynacleGames - Game04 - 2048
#  Last updated:  01/31/25
#  Description: This program uses PyQt5 packages to build the game 2048
import sys
import random
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QGuiApplication
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton
from PyQt5.QtCore import Qt, QTimer
import heapq

# Set game specifications: window size, cell/grid size, cell count, and grid starting location
CELL_COUNT = 4
CELL_SIZE = 150
GRID_ORIGINX = 100
GRID_ORIGINY = 100
W_WIDTH = 800
W_HEIGHT = 800