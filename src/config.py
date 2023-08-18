from enum import Enum

class Origin(Enum):
    ''' Define origin keys '''
    LEFT = 'd'
    RIGHT = 'j'

DEAD_ZONE = 0.3
STILL_SPEED = 0.01
SPEED_THRESH = 0.2
ACC_THRESH = -0.1

BEAM_WIDTH = 10000
