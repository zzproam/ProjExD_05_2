import pygame as pg
import sys
import os
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]


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

