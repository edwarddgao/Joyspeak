import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D
import matplotlib.cm as cm
from controller import XboxController
from keyboard import Keyboard
import numpy as np
from keyboard import Origin

controller = XboxController()
df = Keyboard.pos
interval = 10
colormap = cm.get_cmap('viridis')
fig, ax = plt.subplots(figsize=(10, 5))

# Set up the plot
ax.set_xlim(-1, 11)
ax.set_ylim(-3, 3)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.grid(True)

# Create initial plot with text and point elements
text_elements = []
for row in Keyboard.layout:
    for i, key in enumerate(row['keys']):
        x = row['start_x'] + i
        y = row['y']
        text = ax.text(x, y, key, fontsize=18, ha='center')
        text_elements.append(text)

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
ani = animation.FuncAnimation(fig, update, interval=interval, blit=True)

# Display the plot
plt.show()
