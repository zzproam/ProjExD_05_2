import pygame as pg
import sys
from screen import *
from ship import *
from fuel import *
from score import *
import os
WIDTH, HEIGHT = 1400, 600
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]


def main():
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"{MAIN_DIR}/imgs/bg_ocean.png")
    # クロックの作成
    #scoreの表示
    score = Score()
    score2 = Scores()
    fuels = pg.sprite.Group()
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
             
        #燃料と船が接触したかの判定
        for fuel in fuels:
            if ship1.rect.colliderect(fuel.rect):
                score.score += 20
                fuel.kill()
            if ship2.rect.colliderect(fuel.rect):
                score2.scores += 20
                fuel.kill()
        
        # 背景をブリット
        screen.blit(bg_img, [0, 0])
        # # 300フレームに1回，燃料を出現させる
        if tmr % 4 == 0:
            fuels.add(Fuel())

        ship1.update(key_lst, ship1_controls, screen)
        ship2.update(key_lst, ship2_controls, screen)
        score.update(screen)
        score2.update(screen)
        fuels.draw(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":

    pg.init()
    main()
    pg.quit()
    sys.exit()
