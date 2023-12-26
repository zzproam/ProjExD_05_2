import pygame as pg
import sys
import os
from ship import *
import math
class Lightning(pg.sprite.Sprite):#wasdプレイヤーの爆弾
    imgs = sorted([img for img in os.listdir(f"{MAIN_DIR}/Lightning")])
    def __init__(self,ship: Ship):
        super().__init__()
        self.vx, self.vy = (0,+1)#下方向に
        self.image = [pg.image.load(os.path.join(f"{MAIN_DIR}/Lightning", img)) for img in Lightning.imgs]
        self.rect = self.image[3].get_rect()
        self.rect.centery = ship.rect.centery+ship.rect.height*self.vy
        self.rect.centerx = ship.rect.centerx+ship.rect.width*self.vx
        
