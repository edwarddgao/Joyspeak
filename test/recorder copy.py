from controller import XboxController
import time
import numpy as np
import os

controller = XboxController()
polling_rate = 100

print('Press Right Bumper to start recording path, then again to stop recording path')
while not controller.X:
    target_word = input('Enter target word: ')

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
        np.save(f'saves/{target_word}', path)
        print(f'Saved "{target_word}" to file')
    else:
        print('Path discarded')
    # Wait for A and B to be released
    while controller.A or controller.B:
        time.sleep(0.1)