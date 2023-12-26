#追加機能4
import pygame as pg
import random
import os
#画面サイズ
WIDTH, HEIGHT = 1400, 600
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]

class Fuel(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/imgs/123.jpg"), 0, 0.08)
        self.rect = self.image.get_rect()
        self.rect.center = random.randint(0, WIDTH), random.choice([200,500])