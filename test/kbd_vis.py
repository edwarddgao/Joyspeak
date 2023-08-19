import sys
sys.path.append('..')

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D
import matplotlib.cm as cm
from src.controller import XboxController
from src.keyboard import Keyboard
from src.config import Origin, RADIUS_LIMIT

controller = XboxController()
df = Keyboard.pos
INTERVAL = 10
colormap = cm.get_cmap('viridis')
fig, ax = plt.subplots(figsize=(10, 5))

# Set up the plot
ax.set_xlim(-1, 10)
ax.set_ylim(-1, 4)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_aspect('equal', adjustable='box')
ax.grid(True)

# Create initial plot with text and point elements
text_elements = []
for row in Keyboard.layout:
    for i, key in enumerate(row['keys']):
        x = row['start_x'] + i
        y = row['y']
        text = ax.text(x, y, key, fontsize=18, ha='center')
        text_elements.append(text)

# Get origin coordinates
origin_coords_left = df[df['Key'] == Origin.LEFT.value][['x', 'y']].values[0]
origin_coords_right = df[df['Key'] == Origin.RIGHT.value][['x', 'y']].values[0]

# Create circles at the origin coordinates with radius 2.75
circle_left = plt.Circle(origin_coords_left, RADIUS_LIMIT, color='r', fill=False)
circle_right = plt.Circle(origin_coords_right, RADIUS_LIMIT, color='r', fill=False)

# Add circles to the plot
ax.add_artist(circle_left)
ax.add_artist(circle_right)

# Create line objects for the vectors
line1 = Line2D([0], [0], color='b')
line2 = Line2D([0], [0], color='g')
ax.add_line(line1)
ax.add_line(line2)

# Define an update function that changes the data of the plot
def update(frame):
    # Generate normalized input vectors
    vec_left = controller.get_left_stick()
    vec_right = controller.get_right_stick()
    prob_of_keys = (Keyboard.prob_of_keys(vec_left, Origin.LEFT.value) +
                        Keyboard.prob_of_keys(vec_right, Origin.RIGHT.value)).clip(0, 1)

    # Update the properties of the lines
    for line, vec, origin in [(line1, vec_left, 'd'), (line2, vec_right, 'j')]:
        origin_coords = df[df['Key'] == origin][['x', 'y']].values[0]
        line.set_data([origin_coords[0], origin_coords[0] + vec[0]], [origin_coords[1], origin_coords[1] + vec[1]])

    # Update the color of the keys
    all_keys = [key for row in Keyboard.layout for key in row['keys']]
    for key, text in zip(all_keys, text_elements):
        color_intensity = prob_of_keys[key]
        color = colormap(color_intensity)
        text.set_color(color[:3])  # Set color for text (exclude alpha channel)

    return *text_elements, line1, line2

# Create the animation
ani = animation.FuncAnimation(fig, update, interval=INTERVAL, blit=True)

# Display the plot
plt.show()
