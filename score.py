import os
import random
import sys
import time
import pygame as pg

WIDTH, HEIGHT = 1400, 600

class Score(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.font = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.txt_color = (0, 0, 255)
        self.score = 20
        self.img = self.font.render(f"Ship1燃料:{self.score}", 0, self.txt_color)
        self.rect = self.img.get_rect()
        self.rect.center = (100, HEIGHT - 50)

    def update(self, screen: pg.Surface):
        self.img = self.font.render(f"Ship1燃料:{self.score}", 0, self.txt_color)
        screen.blit(self.img, self.rect)


class Scores(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.font = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.txt_color = (0, 0, 255)
        self.scores = 20
        self.img2 = self.font.render(f"Ship2燃料:{self.scores}", 0, self.txt_color)
        self.rect2 = self.img2.get_rect()
        self.rect2.center = (1300, HEIGHT - 50)

    def update(self, screen: pg.Surface):
        self.img2 = self.font.render(f"Ship2燃料:{self.scores}", 0, self.txt_color)
        screen.blit(self.img2, self.rect2)