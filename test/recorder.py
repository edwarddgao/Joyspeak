import sys
sys.path.append('..')

from src.controller import XboxController
import time
import numpy as np
import os

controller = XboxController()
polling_rate = 100

SAVES_DIR = '../data/.saves'
ENGLISH_TXT = '../data/english.txt'

with open(ENGLISH_TXT, "r") as file:
    words = [line.strip() for line in file]

recorded = [os.path.splitext(filename)[0] for filename in os.listdir(SAVES_DIR) if filename.endswith(".npy")]
print(recorded)

print('Press Right Bumper to start recording path, then again to stop recording path')
for target_word in words:
    if target_word in recorded: continue
    print('Target word:', target_word)

    # Wait for Right Bumper to be pressed
    while not controller.RightBumper:
        time.sleep(0.1)
    # wait for Right Bumper to be released
    while controller.RightBumper:
        time.sleep(0.1)

    print('Recording path...')
    
    path = np.array([[0, 0, 0, 0]], dtype=float)

    # Wait for Right Bumper to be pressed
    while not controller.RightBumper:
        [lx, ly] = controller.get_left_stick()
        [rx, ry] = controller.get_right_stick()
        path = np.append(path, [[lx, ly, rx, ry]], axis=0)

        time.sleep(1/polling_rate)
    # Wait for Right Bumper to be released
    while controller.RightBumper:
        time.sleep(0.1)
    
    print('Press A to save path, or B to discard it')
    # Wait for A or B to be pressed
    while not (controller.A or controller.B):
        time.sleep(0.1)
    if controller.A:
        # save path to file
        np.save(f'{SAVES_DIR}/{target_word}', path)
        print(f'Saved "{target_word}" to file')
    else:
        print('Path discarded')
    # Wait for A and B to be released
    while controller.A or controller.B:
        time.sleep(0.1)