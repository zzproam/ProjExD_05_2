import pygame as pg
import sys
import os
from ship import *
import math
class Bullet1(pg.sprite.Sprite):
    def __init__(self,ship: Ship):
        super().__init__()
        self.vx, self.vy = (0,+1)
        self.image = pg.image.load(f"{MAIN_DIR}/fig/6.png")
        self.rect = self.image.get_rect()
        self.rect.centery = ship.rect.centery+ship.rect.height*self.vy
        self.rect.centerx = ship.rect.centerx+ship.rect.width*self.vx
        self.speed = 10
    
    def update(self):
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)

class Bullet2(pg.sprite.Sprite):
    def __init__(self,ship: Ship):
        super().__init__()
        self.vx, self.vy = (0,-1)
        self.image = pg.image.load(f"{MAIN_DIR}/fig/6.png")
        self.rect = self.image.get_rect()
        self.rect.centery = ship.rect.centery+ship.rect.height*self.vy
        self.rect.centerx = ship.rect.centerx+ship.rect.width*self.vx
        self.speed = 10
    
    def update(self):
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)