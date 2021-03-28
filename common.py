import enum

BUFFER_SIZE = 1024
DEBUG = False


class Messages(enum.Enum):
    none = 'none'
    up = 'up'
    down = 'down'
    left = 'left'
    right = 'right'


class PlayerEnum(enum.Enum):
    musk = 'musk'
    bruno = 'bruno'
    bezos = 'bezos'
    beck = 'beck'


images = {
    PlayerEnum.musk: r'sprites/musk.png',
    PlayerEnum.bruno: r'sprites/bruno.png',
    PlayerEnum.bezos: r'sprites/bezos.png',
    PlayerEnum.beck: r'sprites/beck.png'
}


def debug_print(thing_to_print):
    if DEBUG:
        print(thing_to_print)