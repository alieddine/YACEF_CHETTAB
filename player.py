import random

import pygame




class Player:
    def __init__(self):
        self.player_position = [random.uniform(0, 4), 0, random.uniform(-10, -2)]
