import numpy as np
import pandas as pd
from .config import DEAD_ZONE


class Keyboard:
    ''' Static class representing coordinate system of keyboard layout '''
    layout = [
        {'keys': ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'], 'y': 2, 'start_x': 0},
        {'keys': ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'], 'y': 1, 'start_x': 0.5},
        {'keys': ['z', 'x', 'c', 'v', 'b', 'n', 'm'], 'y': 0, 'start_x': 1},
    ]
    # Generate DataFrame with the keys and their coordinates
    data = []
    for row in layout:
        for i, key in enumerate(row['keys']):
            x = row['start_x'] + i
            y = row['y']
            data.append([key, x, y])
    pos = pd.DataFrame(data, columns=['Key', 'x', 'y'])

    @staticmethod
    def angle_to_keys(vec, origin):
        ''' Return angular difference between vec at origin and each key '''
        # Dead zone
        if np.linalg.norm(vec) < DEAD_ZONE:
            # Return origin key (and empty string later) with probability 0.5
            return pd.Series({origin: np.pi/2})
        
        df = Keyboard.pos
        # Find the coordinates of the origin key
        origin_coords = df[df['Key'] == origin][['x', 'y']].values[0]

        # Exclude origin key from df after checking dead zone
        df = df.loc[df['Key'] != origin].copy()
        
        # Calculate the polar coordinates of the keys relative to the origin
        df['radius'] = np.sqrt((df['x'] - origin_coords[0])**2 + (df['y'] - origin_coords[1])**2)
        df['angle'] = np.arctan2(df['y'] - origin_coords[1], df['x'] - origin_coords[0])
        
        # Filter keys within a certain from the origin
        radius_threshold = 2.75
        df = df[df['radius'] <= radius_threshold]
        
        # Calculate the angular difference to the given vector
        angular_differences = df['angle'] - np.arctan2(vec[1], vec[0])

        # Wrap the angular differences to lie within -pi to pi
        angular_differences = np.arctan2(np.sin(angular_differences), np.cos(angular_differences))

        # Use 'Key' column as index
        angular_differences.index = df['Key']
        return angular_differences

    @staticmethod
    def prob_of_keys(vec, origin):
        # Initialize all keys with 0 probability
        atok = pd.Series(0, index=Keyboard.pos['Key'])
        
        sigma = np.pi/2
        bell_curve = lambda x: np.exp(-x**2 / sigma**2)
        
        # Update probabilities of keys within radius threshold
        atok.update(Keyboard.angle_to_keys(vec, origin).apply(bell_curve))
        
        # Add a key for empty string
        atok[''] = 0.5 if origin in atok.index and atok[origin] > 0 else 0
        
        return atok
