import pygame as pg
import sys
from screen import *
WIDTH, HEIGHT = 1400, 600


def main():
    global WIDTH, HEIGHT
    # 背景インスタンスの作成
    screen = Screen("battleship", WIDTH, HEIGHT, "/Users/patrickdharma/Desktop/プロエン/ProjExD2023/battleship/imgs/bg_ocean.png")
    screen.set_screen()
    # クロックの作成
    clock = pg.time.Clock()
    tmr = 0
    pg.display.update()
    
    while True:
        # イベントハンドラー
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        
        # 背景をブリット
        screen.blit_screen()

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
