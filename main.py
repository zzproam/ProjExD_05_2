import pygame as pg
import sys
from screen import *
from ship import *
import os
WIDTH, HEIGHT = 1400, 600
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]
from pygame.locals import *


class HealthBar():             #ヘルスバークラス
    def __init__(self,x,y,width,max):
        self.x = x
        self.y = y
        self.width = width 
        self.max = max #最大HP
        self.hp = max
        self.mark = int((self.width-4)/self.max) #HPバーの1メモリ

        self.font = pg.font.Font(None, 32)
        self.label = self.font.render("HP",True,(255,255,255))
        self.frame = Rect(self.x + 2 + self.label.get_width(),self.y, self.width,self.label.get_height())   #ヘルスバーのまわり
        self.bar = Rect(self.x + 4 + self.label.get_width(),self.y + 2,self.width -4, self.label.get_height() -4)  #ヘルスバー自体
        self.value = Rect(self.x + 4 + self.label.get_width(),self.y + 2, self.width -4, self.label.get_height() -4)  #ヘルスバーの減ったところ

    def update(self):
        self.value.width = self.hp*self.mark

    def draw(self,screen):
        pg.draw.rect(screen,(255,255,255),self.frame)
        pg.draw.rect(screen,(0,0,0),self.bar)
        pg.draw.rect(screen, (0,255,0),self.value)
        screen.blit(self.label,(self.x,self.y))

    


def main():
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"{MAIN_DIR}/imgs/bg_ocean.png")
    # クロックの作成
    hp_bar = HealthBar(10,10,100,300)

    ship1 = Ship(1, (100, 200))
    ship2 = Ship(7, (1000, 500))
    ship1_controls = {
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (1, 0),
    }
    ship2_controls = {
        pg.K_a: (-1, 0),
        pg.K_d: (1, 0),
    }

    tmr = 0
    clock = pg.time.Clock()

    while True:
        # イベントハンドラー
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        # 背景をブリット
        screen.blit(bg_img, [0, 0])
        hp_bar.draw(screen)
        ship1.update(key_lst, ship1_controls, screen)
        ship2.update(key_lst, ship2_controls, screen)

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":

    pg.init()
    main()
    pg.quit()
    sys.exit()
