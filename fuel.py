import pygame as pg
import random
import os
WIDTH, HEIGHT = 1400, 600
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]


class Fuel(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/1.png"))
        self.rect = self.image.get_rect()
        self.rect.center = random.randint(WIDTH, 200), 0 #燃料の生成
        self.vy = +6

    #def update(self):
