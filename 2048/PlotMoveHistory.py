#  Author: Kyle Tranfaglia
#  Title: PynacleGames - Game04 - 2048
#  Last updated:  03/01/25
#  Description: This program plots the points scored by the AI in respect to the move
import csv
import datetime
import matplotlib.pyplot as plt

# Initialize variables
moves = []
scores = []

# Generate timestamp-based filename
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"2048_progress_{timestamp}.png"

# Read the CSV file
with open("moves.csv", mode='r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header

    for row in reader:
        move, score = int(row[0]), int(row[1])  # Convert data to integers
        moves.append(move)
        scores.append(score)

# Plot the data
plt.figure(figsize=(8, 5))
plt.plot(moves, scores, marker=",", linestyle="-", color="b", label="Score Progression")

# Labels and Title
plt.xlabel("Move Number")
plt.ylabel("Score")
plt.title("2048 AI Score Progression")
plt.legend()
plt.grid(True)

# Save the figure and show the plot
plt.savefig("Plots/" + filename, format="png", dpi=300, bbox_inches="tight")
plt.show()

