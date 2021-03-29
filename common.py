"""
This module holds information that is shared between the client and the server.
"""

import enum

BUFFER_SIZE = 1024  # tcp buffer size
DEBUG = False  # Set to true to enable debugging messages


class Messages(enum.Enum):
    """Enum for the messages that can be sent from the client to the server"""
    none = 'none'
    up = 'up'
    down = 'down'
    left = 'left'
    right = 'right'


class PlayerEnum(enum.Enum):
    """Possible players to choose from"""
    musk = 'musk'
    bruno = 'bruno'
    bezos = 'bezos'
    beck = 'beck'


# Dictionary of where to find images of the players
images = {
    PlayerEnum.musk: r'sprites/musk.png',
    PlayerEnum.bruno: r'sprites/bruno.png',
    PlayerEnum.bezos: r'sprites/bezos.png',
    PlayerEnum.beck: r'sprites/beck.png'
}


def debug_print(thing_to_print):
    """
    Print to console if common.DEBUG is true
    Args:
        thing_to_print (str):  Thing to print
    """
    if DEBUG:
        print(thing_to_print)
