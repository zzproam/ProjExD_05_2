import pygame as pg
import sys
from screen import *
from ship import *
import os
import random
WIDTH, HEIGHT = 1400, 600
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]


class Bird(pg.sprite.Sprite):
    def __init__(self, image_path, xy, frame_count, speed):
        super().__init__()
        self.spritesheet = pg.image.load(
            image_path).convert_alpha()  # ファイル読み込み
        self.frame_count = frame_count
        self.frames = self.load_frames(self.frame_count)
        self.current_frame = 0
        self.animation_speed = 0.2
        # 最初のフレームから
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=xy)
        self.speed = speed

    def load_frames(self, frame_count):
        # spritesheetからフレームを取得
        frames = []
        frame_width = self.spritesheet.get_width() // frame_count
        frame_height = self.spritesheet.get_height()

        for i in range(frame_count):
            frame = self.spritesheet.subsurface(
                (i * frame_width, 0, frame_width, frame_height))
            frames.append(frame)

        return frames

    def animate(self):
        # Sprite動かし
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.frames):
            self.current_frame = 0

        self.image = self.frames[int(self.current_frame)]

    def update(self):
        # アップデート
        self.animate()  # sprite動かし
        self.rect.x += self.speed[0]
        #self.rect.y += self.speed[1]

        if self.rect.right < 0:
            self.rect.left = WIDTH
        if self.rect.left > WIDTH:
            self.rect.right = 0
        if self.rect.bottom < 0:
            self.rect.top = HEIGHT
        if self.rect.top > HEIGHT:
            self.rect.bottom = 0


class Ship(pg.sprite.Sprite):
    """
    船作成
    """

    def __init__(self, num: int, xy: tuple[int, int]):
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(
            f"{MAIN_DIR}/fig/{num}.png"), 0, 1.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (-1, 0): img0,  # 左
        }

        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10

    def update(self, key_lst: list[bool], ctrl_keys: dict, screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in ctrl_keys.items():
            if key_lst[k]:
                self.rect.move_ip(+self.speed*mv[0], +self.speed*mv[1])
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        screen.blit(self.image, self.rect)


class Shield(pg.sprite.Sprite):
    # シールドのクラスを作成
    def __init__(self, ship: Ship, radius: int = 75, color=(0, 0, 255), width=2):
        super().__init__()
        # ship自体、半径、色、幅を設定
        self.ship = ship
        self.radius = radius
        self.color = color
        self.width = width

    def update(self, screen: pg.Surface):
        # 円を描く
        pg.draw.circle(screen, self.color, self.ship.rect.center,
                       self.radius, self.width)


def main():
    # Walk.pngを読み込み
    bird_image_path = os.path.join(MAIN_DIR, 'Walk.png')
    birds = pg.sprite.Group()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"{MAIN_DIR}/imgs/bg_ocean.png")
    bg_img_flipped = pg.transform.flip(bg_img, True, False)
    bg_x = 0
    bg_x_flipped = bg_img.get_width()

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
    for _ in range(5):  # 鳥数が５に
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        # スピードをランダムに
        speed_x = random.choice([1, 2, 3])
        speed_y = random.choice([-3, -2, -1, 1, 2, 3])
        bird = Bird(bird_image_path, (x, y), frame_count=6,
                    speed=(speed_x, speed_y))
        birds.add(bird)

    ship1_shield = Shield(ship1)
    ship2_shield = Shield(ship2)

    tmr = 0
    clock = pg.time.Clock()

    while True:
        bg_x -= 1
        bg_x_flipped -= 1
        # イベントハンドラー
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
         # 背景をブリット
        if bg_x < -bg_img.get_width():
            bg_x = bg_img.get_width()
        if bg_x_flipped < -bg_img.get_width():
            bg_x_flipped = bg_img.get_width()
        screen.blit(bg_img, (bg_x, 0))
        screen.blit(bg_img_flipped, (bg_x_flipped, 0))

        ship1.update(key_lst, ship1_controls, screen)
        ship2.update(key_lst, ship2_controls, screen)
        if key_lst[pg.K_DOWN]:
            ship1_shield.update(screen)
        if key_lst[pg.K_s]:
            ship2_shield.update(screen)

        birds.update()  # 鳥をアップデート
        birds.draw(screen)

        pg.display.update()
        tmr += 1
        clock.tick(50)
#


if __name__ == "__main__":

    pg.init()
    main()
    pg.quit()
    sys.exit()
