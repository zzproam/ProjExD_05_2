import pygame as pg
import sys
from screen import *
from ship import *
import os
from Bullet import *
WIDTH, HEIGHT = 1400, 600
pg.display.set_caption('BattleShip')
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]

class Lightning1(pg.sprite.Sprite):
    imgs = sorted([img for img in os.listdir(f"{MAIN_DIR}/Lightning")])

    def __init__(self, ship: Ship):
        super().__init__()
        self.images = [pg.image.load(os.path.join(f"{MAIN_DIR}/Lightning", img)) for img in Lightning1.imgs]
        
        # Scale the images to be twice as big
        self.images = [pg.transform.scale(img, (img.get_width() * 2, img.get_height() * 2)) for img in self.images]

        self.current_frame = 0
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect()
        
        # Positioning the lightning to come out from the bottom of the ship
        self.rect.centerx = ship.rect.centerx
        self.rect.top = ship.rect.bottom  # Align the top of the lightning with the bottom of the ship
        self.animation_done = False
    def update(self):
        self.current_frame = (self.current_frame + 1) % len(self.images)
        self.image = self.images[self.current_frame]

        if self.current_frame == 0:
                self.animation_done = True

class Lightning2(pg.sprite.Sprite):
    imgs = sorted([img for img in os.listdir(f"{MAIN_DIR}/Lightning")])

    def __init__(self, ship: Ship):
        super().__init__()
        # Load and flip images vertically
        self.images = [pg.transform.flip(pg.image.load(os.path.join(f"{MAIN_DIR}/Lightning", img)), False, True) for img in Lightning2.imgs]

        # Scale the flipped images to be twice as big
        self.images = [pg.transform.scale(img, (img.get_width() * 2, img.get_height() * 2)) for img in self.images]

        self.current_frame = 0
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect()
        self.speed = -10
        # Position the lightning at the bottom of the ship
        self.rect.centerx = ship.rect.centerx
        self.rect.bottom = ship.rect.top  # Align the top of the lightning with the bottom of the ship
        self.animation_done = False

    def update(self):
        self.current_frame = (self.current_frame + 1) % len(self.images)
        self.image = self.images[self.current_frame]
        self.rect.y += self.speed
        if self.current_frame == 0:
            self.animation_done = True

def main():
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"{MAIN_DIR}/imgs/bg_ocean.png")
    # クロックの作成

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
    bullets = pg.sprite.Group()
    lightnings = pg.sprite.Group()
    tmr = 0
    clock = pg.time.Clock()

    while True:
        # イベントハンドラー
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_RIGHTBRACKET:
                bullets.add(Bullet1(ship1))
            if event.type == pg.KEYDOWN and event.key == pg.K_g:
                bullets.add(Bullet2(ship2))
            if event.type == pg.KEYDOWN and event.key == pg.K_RSHIFT:
                lightnings.add(Lightning1(ship1))
            if event.type == pg.KEYDOWN and event.key == pg.K_h:
                lightnings.add(Lightning2(ship2))
        # 背景をブリット
        screen.blit(bg_img, [0, 0])

        ship1.update(key_lst, ship1_controls, screen)
        ship2.update(key_lst, ship2_controls, screen)
        bullets.update()
        bullets.draw(screen)
        lightnings.update()
        lightnings.draw(screen)
        for lightning in list(lightnings):
            if lightning.animation_done:
                lightnings.remove(lightning)
        pg.display.update()
        tmr += 1
        clock.tick(50)

if __name__ == "__main__":

    pg.init()
    main()
    pg.quit()
    sys.exit()
