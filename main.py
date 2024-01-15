import pygame as pg
import sys
from screen import *
from ship import *
from score import *
from fuel import *
import os
import random
import time
from pygame.locals import *
WIDTH, HEIGHT = 1600, 900
pg.display.set_caption('BattleShip')
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]

idle_image_paths = {
    1: 'Idle1.png',  
    2: 'Idle2.png'   
}
move_image_paths = {
    1: 'Move1.png',  
    2: 'Move2.png'   
}


def restrict_ship_movement(ship, ship_num):
    # 異なる船の境界を定義する辞書
    ship_bounds = {
        1: (0, 0, WIDTH, 400),   # 船1の境界：(左、上、右、下)
        2: (0, 500, WIDTH, HEIGHT)  # 船2の境界：(左、上、右、下)
    }

    # ship_numに基づいて船の境界を取得；見つからない場合はデフォルト値を使用
    min_x, min_y, max_x, max_y = ship_bounds.get(
        ship_num, (0, 0, WIDTH, HEIGHT))

    # 船の左、上、右、下の位置が境界内にあることを確認
    ship.rect.left = max(min_x, min(ship.rect.left, max_x))
    ship.rect.top = max(min_y, min(ship.rect.top, max_y))
    ship.rect.right = min(max_x, max(ship.rect.right, min_x))
    ship.rect.bottom = min(max_y, max(ship.rect.bottom, min_y))


class Explosion(pg.sprite.Sprite):
    """
    キャラクターが死んだ時に爆発アニメーションを起動する
    """

    def __init__(self, center, size=(100, 100)):
        super().__init__()
        # 爆発画像のリストを初期化
        self.images = []
        # 爆発画像を読み込むメソッドを呼び出す
        self.load_images()
        # 現在のフレーム番号を初期化
        self.current_frame = 0
        # 最初の爆発画像を設定
        self.image = self.images[self.current_frame]
        # 爆発画像の位置と大きさを設定
        self.rect = self.image.get_rect(center=center)
        # フレーム数をカウントする変数を初期化
        self.frame_count = 0
        # アニメーションの速度を設定
        self.animation_speed = 1
        # アニメーションの総フレーム数を設定
        self.total_frames = 10 * 5

    def load_images(self):
        # 爆発画像を読み込む
        for i in range(1, 11):
            # 各爆発画像を読み込む
            img = pg.image.load(
                f'{MAIN_DIR}/fig/Explosion_{i}.png').convert_alpha()
            # 画像のサイズを調整
            img = pg.transform.scale(img, (100, 100))
            # 画像をリストに追加
            self.images.append(img)

    def update(self):
        # アニメーションを更新する
        if self.frame_count < self.total_frames or self.current_frame < len(self.images) - 1:
            # 現在のフレームを計算
            self.current_frame = (self.frame_count // 5) % len(self.images)
            # 現在の画像を更新
            self.image = self.images[int(self.current_frame)]
            # フレームカウントを増加
            self.frame_count += 1
        else:
            # アニメーションが終了したら、スプライトを削除
            self.kill()


class Blink(pg.sprite.Sprite):
    """
    プレイヤーの能力である瞬間移動を管理するクラスです。
    """
    def __init__(self, ship: Ship, image_path, frame_count):
        super().__init__()
        self.ship = ship
        self.spritesheet = pg.image.load(image_path).convert_alpha()
        self.frame_count = frame_count
        self.frames = self.load_frames(self.frame_count)
        self.current_frame = 0
        self.animation_speed = 1
        self.active = False  # 瞬間移動がアクティブかどうかを示すフラグ

    def animate(self):
        if self.active:
            self.current_frame += self.animation_speed
            if self.current_frame >= len(self.frames):
                self.current_frame = 0
            self.image = self.frames[int(self.current_frame)]
            self.rect = self.image.get_rect(center=self.ship.rect.center)

    def start_blink(self, direction):
        self.active = True
        self.ship.blinking = True  # シップに点滅中であることを知らせる
        self.ship.blink_direction = direction
        self.current_frame = 0  # アニメーションフレームをリセット

        # 瞬間移動の方向が左の場合、アニメーションフレームを反転させる
        self.frames = [pg.transform.flip(
            frame, True, False) if direction[0] < 0 else frame for frame in self.original_frames]

    def stop_blink(self):
        self.active = False
        self.ship.blinking = False  # シップに点滅が終わったことを知らせる

    def load_frames(self, frame_count):
        # スプライトシートをフレームに分割し、new_sizeが指定されていればリサイズします。
        frames = []
        frame_width = self.spritesheet.get_width() // frame_count
        frame_height = self.spritesheet.get_height()
        for i in range(frame_count):
            frame = self.spritesheet.subsurface(
                (i * frame_width, 0, frame_width, frame_height))
            frame = pg.transform.rotozoom(frame, 225, 1.0)
            frames.append(frame)
        # 反転用に元のフレームを保存
        self.original_frames = list(frames)
        return frames

    def update(self, screen: pg.Surface):
        self.animate()
        if self.active:
            # アニメーションをシップのrectの端に配置します（方向に基づいて）
            if self.ship.blink_direction[0] > 0:  # 左に移動している場合
                self.rect.right = self.ship.rect.left
            else:  # 右に移動している場合
                self.rect.left = self.ship.rect.right
            screen.blit(self.image, self.rect)


class Bird(pg.sprite.Sprite):
    """
    背景のデコレーションとして、鳥のインスタンスを管理するクラスです。
    """
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
    プレイヤーのキャラクターを管理するクラスです。
    """
    def __init__(self, num: int, xy: tuple[int, int], idle_frames, move_frames, ship_num, new_size):
        super().__init__()

        # アイドルと移動の画像を読み込む
        self.idle_images = self.load_images(
            f"{MAIN_DIR}/fig/Idle{num}.png", idle_frames, new_size)
        self.move_images = self.load_images(
            f"{MAIN_DIR}/fig/Move{num}.png", move_frames, new_size)
        self.images = self.idle_images  # 最初はアイドル画像から開始
        self.current_frame = 0
        self.animation_speed = 0.2
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect(center=xy)

        # ヒットボックスのオフセットとサイズを設定
        hitbox_offset = 0.45
        self.hitbox = self.rect.inflate(
            self.rect.width * (hitbox_offset - 1),
            self.rect.height * (hitbox_offset - 1)
        )

        self.speed = 10
        self.moving = False  # シップが移動しているかどうかを示す
        self.moving_left = False  # シップが左に移動しているかどうかを示す

        self.blinking = False
        self.blink_distance = 500  # 更新された点滅距離
        self.blink_direction = (1, 0)  # デフォルトの点滅方向は右

        self.last_direction = (+1, 0)

        self.blink_speed = 20  # シップが1フレームあたりに点滅する速さ

        self.ship_num = ship_num

    def load_images(self, image_path, frame_count, new_size=None):
        images = []
        spritesheet = pg.image.load(image_path).convert_alpha()
        frame_width = spritesheet.get_width() // frame_count
        frame_height = spritesheet.get_height()
        for i in range(frame_count):
            frame = spritesheet.subsurface(
                (i * frame_width, 0, frame_width, frame_height))
            if new_size:
                frame = pg.transform.scale(frame, new_size)
            images.append(frame)
        return images

    def animate(self):
        # アニメーションの更新
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.images):
            self.current_frame = 0
        self.image = self.images[int(self.current_frame)]
        if self.moving and self.moving_left:
            self.image = pg.transform.flip(self.image, True, False)

    def update(self, key_lst: list[bool], ctrl_keys: dict, screen: pg.Surface):
        self.moving = False  # 移動状態をリセット
        sum_mv = [0, 0]
        if not self.blinking:
            for k, mv in ctrl_keys.items():
                if key_lst[k]:
                    # 移動キーが押されていれば、シップを移動させる
                    self.rect.move_ip(+self.speed*mv[0], +self.speed*mv[1])
                    sum_mv[0] += mv[0]
                    sum_mv[1] += mv[1]
                    self.moving = True
                    self.moving_left = mv[0] < 0
                if sum_mv != [0, 0]:
                    # 移動中の場合は最後の移動方向を更新
                    self.last_direction = (sum_mv[0], sum_mv[1])
        else:
            # 点滅中の移動コード
            self.rect.x += self.blink_direction[0] * self.blink_speed
            self.blink_distance -= self.blink_speed
            if self.blink_distance <= 0:
                self.blinking = False
                self.blink_distance = 500  # 点滅距離をリセット
                self.blink_direction = (1, 0)  # 点滅方向をリセット
                # Blinkインスタンスのstop_blinkメソッドをトリガーする
                self.blink_instance.stop_blink()

        if self.moving:
            self.images = self.move_images
        else:
            self.images = self.idle_images
        restrict_ship_movement(self, self.ship_num)
        self.hitbox.center = self.rect.center
        self.animate()
        screen.blit(self.image, self.rect)


class Shield(pg.sprite.Sprite):
    """
    プレイヤーをbulletやlightningの攻撃から守るシールドを表すクラスです。
    """
    def __init__(self, ship: Ship, image_path=None, frame_count=0, new_size=None, radius=75, color=(0, 0, 255), width=2):
        super().__init__()

        self.ship = ship  # シールドを所有するプレイヤーシップ
        self.radius = radius  # シールドの半径
        self.color = color  # シールドの色
        self.width = width  # シールドの線の太さ
        self.is_animated = image_path is not None and frame_count > 0

        if self.is_animated:
            # アニメーション用のスプライトシートを読み込む
            self.spritesheet = pg.image.load(image_path).convert_alpha()
            self.frame_count = frame_count
            self.frames = self.load_frames(frame_count, new_size)
            self.current_frame = 0
            self.animation_speed = 0.2
            self.image = self.frames[self.current_frame]
            self.rect = self.image.get_rect(center=self.ship.rect.center)
        else:
            self.image = None
            self.rect = None

    def load_frames(self, frame_count, new_size):
        frames = []
        frame_width = self.spritesheet.get_width() // frame_count
        frame_height = self.spritesheet.get_height()

        # スプライトシートからフレームをロードしてリサイズ
        for i in range(frame_count):
            frame = self.spritesheet.subsurface(
                (i * frame_width, 0, frame_width, frame_height))
            if new_size:
                frame = pg.transform.scale(frame, new_size)
            frames.append(frame)
        return frames

    def animate(self):
        # アニメーションの更新
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.frames):
            self.current_frame = 0
        self.image = self.frames[int(self.current_frame)]
        self.rect = self.image.get_rect(center=self.ship.rect.center)

    def update(self, screen: pg.Surface):
        # シールドの表示を更新
        if self.is_animated:
            self.animate()
            screen.blit(self.image, self.rect)
        else:
            # 静止画の場合は円でシールドを描画
            pg.draw.circle(screen, self.color,
                           self.ship.rect.center, self.radius, self.width)


class Bullet(pg.sprite.Sprite):
    """
    プレイヤーの軽いアタックを表すクラス。ドーナツを投げます。
    """
    def __init__(self, ship: Ship, direction: str):
        super().__init__()

        # 画像を読み込み、中心の座標を設定
        self.image = pg.image.load(f"{MAIN_DIR}/fig/6.png")
        self.rect = self.image.get_rect(center=(ship.rect.centerx,
                                                ship.rect.top if direction == "up" else ship.rect.bottom))

        self.speed = 10  # 弾の速さ

        self.ship_num = ship.ship_num  # 弾を発射した船を識別する属性

        # 方向に基づいて速度を設定
        if direction == "up":
            self.vx, self.vy = (0, -1)
        elif direction == "down":
            self.vx, self.vy = (0, 1)
        else:
            raise ValueError(
                "弾の方向が無効です。'up' または 'down' を選択してください。")

    def update(self):
        # 弾を速度に従って移動させる
        self.rect.move_ip(self.speed * self.vx, self.speed * self.vy)

        # 弾が画面外に出たら削除
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()


class Lightning(pg.sprite.Sprite):
    """
    プレイヤーの必殺技であるライトニングを管理するクラスです。
    """
    def __init__(self, ship: Ship, direction: str):
        super().__init__()

        # 画像を方向に基づいて読み込む
        self.load_images(direction)

        self.current_frame = 0
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect(centerx=ship.rect.centerx)

        # ライトニングの初期位置を設定
        if direction == "up":
            self.rect.bottom = ship.rect.top
        elif direction == "down":
            self.rect.top = ship.rect.bottom
        else:
            raise ValueError(
                "ライトニングの方向が無効です。'up' または 'down' を選択してください。")

        self.animation_done = False  # アニメーションが完了したかどうかのフラグ

    def load_images(self, direction):
        # 画像のリストを読み込む
        imgs = sorted([img for img in os.listdir(f"{MAIN_DIR}/Lightning")])
        self.images = []

        for img in imgs:
            # 画像を透過可能なアルファチャンネル付きで読み込む
            image = pg.image.load(os.path.join(
                f"{MAIN_DIR}/Lightning", img)).convert_alpha()

            # 画像を2倍のサイズに拡大
            image = pg.transform.scale(
                image, (image.get_width() * 2, image.get_height() * 2))

            # 上向きの方向の場合、画像を反転させる
            if direction == "up":
                image = pg.transform.flip(image, False, True)

            self.images.append(image)

    def update(self):
        # フレームを更新
        self.current_frame = (self.current_frame + 1) % len(self.images)
        self.image = self.images[self.current_frame]

        # アニメーションが最初のフレームに戻ったらアニメーションを終了する
        if self.current_frame == 0:
            self.animation_done = True


class Explosion2(pg.sprite.Sprite):
    """
    爆発2のアニメーションを管理するクラスです。lightningとplayerが衝突する時の爆発アニメーションです。
    """
    def __init__(self, position):
        super().__init__()

        # 画像リストの読み込み
        self.images = [pg.image.load(
            f"{MAIN_DIR}/Explosion_two_colors/Explosion_two_colors{frame}.png") for frame in range(1, 11)]

        self.current_frame = 0
        self.image = self.images[self.current_frame]  # 最初の画像を設定
        self.rect = self.image.get_rect(center=position)
        self.animation_done = False  # アニメーションが完了したかどうかのフラグ

    def update(self):
        # フレームを更新
        self.current_frame += 1
        # すべてのフレームが表示されたらアニメーションを終了
        if self.current_frame < len(self.images):
            self.image = self.images[self.current_frame]
        else:
            self.animation_done = True  # すべてのフレームが表示されたらアニメーションを終了する


class HealthBar():
    """
    プレイヤーのヘルスバーを管理するクラスです。
    """
    def __init__(self, x, y, width, max_hp):
        # 初期化メソッド
        self.x = x
        self.y = y
        self.width = width
        self.max_hp = max_hp  # 最大ヘルスを100に設定
        self.hp = max_hp
        self.mark = self.width / self.max_hp  # 各ヘルスポイントの幅を計算

        # フォントとラベルの設定
        self.font = pg.font.Font(None, 32)
        self.label = self.font.render("HP", True, (255, 255, 255))

        # バーと値の矩形の初期化
        self.frame = pg.Rect(self.x + 2 + self.label.get_width(),
                             self.y, self.width, self.label.get_height())
        self.bar = pg.Rect(self.x + 4 + self.label.get_width(),
                           self.y + 2, self.width - 4, self.label.get_height() - 4)
        self.value = pg.Rect(self.x + 4 + self.label.get_width(),
                             self.y + 2, self.width - 4, self.label.get_height() - 4)

        # エフェクトカラーの設定（ヘルスバーの色）
        self.effect_color = (0, 255, 0)  # ヘルスバーの色を緑に設定

    def decrease(self, amount):
        # ヘルスを指定された量だけ減少させ、バーの幅を更新
        self.hp = max(self.hp - amount, 0)
        self.value.width = self.mark * self.hp  

    def update(self):
        # ヘルスバーを更新するための追加のロジック（あれば）
        pass

    def draw(self, screen):
        # ヘルスバーを描画
        pg.draw.rect(screen, (255, 255, 255), self.frame)
        pg.draw.rect(screen, (0, 0, 0), self.bar)
        pg.draw.rect(screen, self.effect_color, self.value)
        screen.blit(self.label, (self.x, self.y))


class Fuel(pg.sprite.Sprite):
    """
    燃料のクラスです。playerが燃料を取ると、燃料の補充になるます。
    """
    def __init__(self):
        super().__init__()
        self.image = pg.transform.rotozoom(
            pg.image.load(f"{MAIN_DIR}/imgs/123.jpg"), 0, 0.08)
        self.rect = self.image.get_rect()
        self.rect.center = random.randint(0, WIDTH), random.choice([200, 500])


class FuelBar():
    """
    燃料の状態を表すクラスです。燃料がないと、さまざまな機能ができなくなります。
    """
    def __init__(self, x, y, width, max_fuel):
        # バーの位置とサイズの初期化
        self.x = x
        self.y = y
        self.width = width
        self.max_fuel = max_fuel  
        self.fuel = max_fuel
        self.mark = self.width / self.max_fuel  

        # テキストやバーのデザイン関連の初期化
        self.font = pg.font.Font(None, 32)
        self.label = self.font.render("Fuel", True, (255, 255, 255))
        self.frame = pg.Rect(self.x + 2 + self.label.get_width(),
                             self.y, self.width, self.label.get_height())
        self.bar = pg.Rect(self.x + 4 + self.label.get_width(),
                           self.y + 2, self.width - 4, self.label.get_height() - 4)
        self.value = pg.Rect(self.x + 4 + self.label.get_width(),
                             self.y + 2, self.width - 4, self.label.get_height() - 4)
        self.effect_color = (255, 255, 0)  

    def decrease(self, amount):
        # 燃料を減少させ、バーの幅を更新
        self.fuel = max(self.fuel - amount, 0)
        self.value.width = self.mark * self.fuel  

    def increase(self, amount):
        # 燃料を増加させ、バーの幅を更新
        self.fuel = min(self.fuel + amount, self.max_fuel)
        self.value.width = self.mark * self.fuel  

    def draw(self, screen):
        # バーを描画
        pg.draw.rect(screen, (255, 255, 255), self.frame)
        pg.draw.rect(screen, (0, 0, 0), self.bar)
        pg.draw.rect(screen, self.effect_color, self.value)
        
        # テキストを描画
        screen.blit(self.label, (self.x, self.y))


def main():
    """
    この関数はゲームのメインループを含んでいます。画面の初期化、スプライトの作成、UI要素の設定、背景の初期化などのゲームの主要な部分がこの関数で実行されます。
    """
    screen = initialize_screen()
    birds, ships, bullets, lightnings, explosions, explosion2s, fuels, ship1, ship2, ship1_blink, ship2_blink, ship1_shield, ship2_shield = initialize_sprites()
    hp_bar1, hp_bar2, fuel_bar1, fuel_bar2 = initialize_ui_elements()
    bg_img, bg_img_flipped, bg_x, bg_x_flipped, bg_tile_width, bg_tile_height, tiles_x, tiles_y = initialize_background()
    game_over = False
    clock = pg.time.Clock()
    tmr = 0
    while not game_over:
        bg_x, bg_x_flipped = handle_background_movement(
            bg_x, bg_x_flipped, bg_tile_width, bg_tile_height, tiles_x, tiles_y, screen, bg_img, bg_img_flipped)
        key_states = pg.key.get_pressed()  
        handle_events(pg.event.get(), key_states, ships, bullets, lightnings,
                      ship1_blink, ship2_blink, fuel_bar1, fuel_bar2)

        update_state = update_game_state(ships, bullets, lightnings, explosion2s, explosions, fuels, birds, tmr,
                                          ship1, ship2, ship1_blink, ship2_blink, key_states, screen, hp_bar1, hp_bar2, fuel_bar1, fuel_bar2)

        draw_game_state(screen, ships, bullets, lightnings, explosions, explosion2s, birds, fuels,
                        hp_bar1, hp_bar2, ship1_shield, ship2_shield, key_states, fuel_bar1, fuel_bar2)
        if update_state:
            display_end_game_result(screen, hp_bar1, hp_bar2)
            break

        pg.display.update()
        tmr += 1
        clock.tick(50)

    pg.time.delay(3000)
    pg.quit()


def initialize_screen():
    """
    画面の初期設定を行います。画面サイズを設定し、ウィンドウのタイトルを設定します。
    """
    screen = pg.display.set_mode((WIDTH, HEIGHT))  # Pygameの表示画面オブジェクト
    pg.display.set_caption('ケーキ泥棒')
    return screen


def initialize_sprites():
    """
    ゲームで使用するスプライト（キャラクターやオブジェクト）を初期化します。
    """
    bird_image_path = os.path.join(MAIN_DIR, 'fig/Walk.png')  # 鳥のスプライト画像のパス。
    birds = pg.sprite.Group()  # 鳥のスプライトを格納するグループ。
    for _ in range(5):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        speed_x = random.choice([1, 2, 3])
        speed_y = random.choice([-3, -2, -1, 1, 2, 3])
        bird = Bird(bird_image_path, (x, y), frame_count=6,
                    speed=(speed_x, speed_y))
        birds.add(bird)

    ship1_frame_count_idle = 20
    ship1_frame_count_move = 20
    ship2_frame_count_idle = 27
    ship2_frame_count_move = 27

    # 2つの船のスプライトを初期化する
    ship1 = Ship(1, (100, 200), ship1_frame_count_idle,
                 ship1_frame_count_move, ship_num=1, new_size=(150, 150))
    ship2 = Ship(2, (1000, 500), ship2_frame_count_idle,
                 ship2_frame_count_move, ship_num=2, new_size=(150, 150))

    # shieldインスタンスの初期化
    shield1_sprite_path = os.path.join(MAIN_DIR, 'fig/shield1.png')  # shield1のパス
    shield1_frame_count = 8  # shield1スプライトシートのフレーム数
    shield2_sprite_path = os.path.join(MAIN_DIR, 'fig/shield2.png')  # shield2のパス
    shield2_frame_count = 7  # shield2スプライトシートのフレーム数
    ship1_shield = Shield(ship1, shield1_sprite_path,
                          shield1_frame_count, new_size=(300, 300))
    ship2_shield = Shield(ship2, shield2_sprite_path,
                          shield2_frame_count, new_size=(300, 300))
    
    # Blinkオブジェクトの初期化
    blink_frame_count_ship1 = 8
    blink_frame_count_ship2 = 8
    # 瞬間移動オブジェクトの画像パス
    blink_image_path_ship1 = os.path.join(
        MAIN_DIR, 'fig/blink.png')  
    blink_image_path_ship2 = os.path.join(
        MAIN_DIR, 'fig/blink.png')  
    ship1_blink = Blink(ship1, blink_image_path_ship1, blink_frame_count_ship1)
    ship2_blink = Blink(ship2, blink_image_path_ship2, blink_frame_count_ship2)

    # ShipsにBlinkのインスタンスを割り当てます
    ship1.blink_instance = ship1_blink
    ship2.blink_instance = ship2_blink

    # スプライトグループの初期化
    ships = pg.sprite.Group(ship1, ship2)
    bullets = pg.sprite.Group()
    lightnings = pg.sprite.Group()
    explosions = pg.sprite.Group()
    explosion2s = pg.sprite.Group()
    fuels = pg.sprite.Group()
    # 新しいインスタンスを含めてreturn文を更新します
    return birds, ships, bullets, lightnings, explosions, explosion2s, fuels, ship1, ship2, ship1_blink, ship2_blink, ship1_shield, ship2_shield


def initialize_ui_elements():
    """
    UI要素(ヘルスバー、燃料表示)を初期化します。プレイヤー1のヘルスバーと燃料バーは画面の左上に、プレイヤー2のヘルスバーと燃料バーは画面の右上に表示されます。
    """
    hp_bar1 = HealthBar(10, 10, 100, 1000)  # x, y, width, max
    hp_bar2 = HealthBar(WIDTH - 200, 10, 100, 1000)  # x, y, width, max
    fuel_bar1 = FuelBar(10, 50, 100, 100)  # hp_bar1の下に配置, (x, y, width, max)
    fuel_bar2 = FuelBar(WIDTH - 200, 50, 100, 100)  # hp_bar2の下に配置, (x, y, width, max)
    return hp_bar1, hp_bar2, fuel_bar1, fuel_bar2


def initialize_background():
    """
    背景画像と関連設定を初期化します。
    """
    # 背景画像の元データをロード
    bg_img_original = pg.image.load(f"{MAIN_DIR}/imgs/bg_ocean.png")
    
    # 画面サイズに背景画像を拡大縮小
    bg_img = pg.transform.scale(bg_img_original, (WIDTH, HEIGHT))
    
    # 背景画像を反転させた画像を作成
    bg_img_flipped = pg.transform.flip(bg_img, True, False)
    
    # 背景のX座標と反転後のX座標の初期化
    bg_x = 0
    bg_x_flipped = bg_img.get_width()
    
    # 背景タイルの幅と高さの取得
    bg_tile_width = bg_img.get_width()
    bg_tile_height = bg_img.get_height()
    
    # 背景のタイルが何枚必要か計算
    tiles_x = -(-WIDTH // bg_tile_width) + 1
    tiles_y = -(-HEIGHT // bg_tile_height)
    
    # 初期化した背景関連のパラメータを返す
    return bg_img, bg_img_flipped, bg_x, bg_x_flipped, bg_tile_width, bg_tile_height, tiles_x, tiles_y


def handle_background_movement(bg_x, bg_x_flipped, bg_tile_width, bg_tile_height, tiles_x, tiles_y, screen, bg_img, bg_img_flipped):
    """
    背景の動きを制御します。背景画像をスクロールさせることで、動いているように見せます。
    """
    # 背景画像のX座標を更新
    bg_x -= 1
    bg_x_flipped -= 1

    # 背景画像が画面外に移動した場合、ループさせて繰り返し利用
    if bg_x < -bg_tile_width:
        bg_x = bg_tile_width
    if bg_x_flipped < -bg_tile_width:
        bg_x_flipped = bg_tile_width

    # 背景画像を繰り返し敷き詰めてスクロール効果を再現
    for y in range(tiles_y):
        for x in range(tiles_x):
            screen.blit(bg_img, (x * bg_tile_width + bg_x, y * bg_tile_height))
            screen.blit(bg_img_flipped, (x * bg_tile_width +
                        bg_x_flipped, y * bg_tile_height))

    # 更新された背景画像のX座標を返す
    return bg_x, bg_x_flipped


def handle_events(events, key_states, ships, bullets, lightnings, ship1_blink, ship2_blink, fuel_bar1, fuel_bar2):
    """
    キーボードやマウスなどのユーザー入力イベントを処理します。
    """
    
    # プレイヤー1およびプレイヤー2の船オブジェクトを取得
    ship1 = next((ship for ship in ships if ship.ship_num == 1), None)
    ship2 = next((ship for ship in ships if ship.ship_num == 2), None)

    for event in events:
        if event.type == pg.QUIT:
            # ゲーム終了イベントの場合、Pygameを終了しプログラムを終了
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            
            # キーボードが押されたときの処理
            if event.key == pg.K_RIGHTBRACKET:
                # プレイヤー1が右ブラケットキーを押したとき、新しい弾を発射
                if ship1:
                    bullets.add(Bullet(ship1, "down"))
            elif event.key == pg.K_g:
                # プレイヤー2が 'g' キーを押したとき、新しい弾を発射
                if ship2:
                    bullets.add(Bullet(ship2, "up"))
            
            elif event.key == pg.K_LEFTBRACKET:
                # プレイヤー1が左ブラケットキーを押したとき、新しいライトニングを発射
                if fuel_bar1.fuel > 0:
                    lightnings.add(Lightning(ship1, "down"))
                    fuel_bar1.decrease(10) 
            elif event.key == pg.K_h:
                # プレイヤー2が 'h' キーを押したとき、新しいライトニングを発射
                if fuel_bar2.fuel > 0:
                    lightnings.add(Lightning(ship2, "up"))
                    fuel_bar2.decrease(10)
            
            elif event.key == pg.K_LSHIFT:
                # プレイヤー2が左シフトキーを押したとき、Blinkを開始
                direction = (-1, 0) if key_states[pg.K_a] else (1, 0)
                if not ship2.blinking:
                    if fuel_bar2.fuel > 0:
                        ship2_blink.start_blink(direction)
                        fuel_bar2.decrease(30)
            elif event.key == pg.K_RSHIFT:
                # プレイヤー1が右シフトキーを押したとき、Blinkを開始
                direction = (-1, 0) if key_states[pg.K_LEFT] else (1, 0)
                if not ship1.blinking:
                    if fuel_bar1.fuel > 0:
                        ship1_blink.start_blink(direction)
                        fuel_bar1.decrease(20)


def handle_collisions(ships, bullets, lightnings, explosion2s, explosions, fuels, tmr, hp_bar1, hp_bar2, fuel_bar1, fuel_bar2):
    """
    スプライト間の衝突を検出し、それに応じた処理を行います。
    """
    # shipsスプライトグループからship1およびship2を取得
    ship1 = next((ship for ship in ships if ship.ship_num == 1), None)
    ship2 = next((ship for ship in ships if ship.ship_num == 2), None)

    # 弾と船の衝突
    for bullet in list(bullets):
        if ship1 and bullet.rect.colliderect(ship1.hitbox) and bullet.ship_num != ship1.ship_num:
            # 船1に対する衝突処理
            explosions.add(Explosion(ship1.rect.center, size=(100, 100)))
            bullets.remove(bullet)
            hp_bar1.decrease(10)
            fuel_bar1.decrease(10)  # 船1の燃料を減少
            fuel_bar2.decrease(10)  # 船2の燃料を減少
        elif ship2 and bullet.rect.colliderect(ship2.hitbox) and bullet.ship_num != ship2.ship_num:
            # 船2に対する衝突処理
            explosions.add(Explosion(ship2.rect.center, size=(100, 100)))
            bullets.remove(bullet)
            hp_bar2.decrease(10)

    # ライトニングと船の衝突
    if ship1:
        for lightning in lightnings:
            if ship1.hitbox.colliderect(lightning):
                # 船1に対する衝突処理
                explosion2s.add(Explosion2(ship1.rect.center))
                hp_bar1.decrease(10)
    if ship2:
        for lightning in lightnings:
            if ship2.hitbox.colliderect(lightning.rect):
                # 船2に対する衝突処理
                explosion2s.add(Explosion2(ship2.rect.center))
                hp_bar2.decrease(10)

    # 燃料の取得とスコアの更新
    for fuel in list(fuels):
        if ship1 and ship1.rect.colliderect(fuel.rect):
            # 燃料を増加
            fuel_bar1.increase(10)
            fuel.kill()
        elif ship2 and ship2.rect.colliderect(fuel.rect):
            fuel_bar2.increase(10)
            fuel.kill()


def update_game_state(ships, bullets, lightnings, explosion2s, explosions, fuels, birds, tmr, ship1, ship2, ship1_blink, ship2_blink, key_states, screen, hp_bar1, hp_bar2, fuel_bar1, fuel_bar2):
    """
    ゲームの状態を更新します。スプライトの移動、アニメーションの更新などが含まれます。
    """
    # 船のコントロールのためのグローバル定義
    ship1_controls = {
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, 1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (1, 0),
    }

    ship2_controls = {
        pg.K_w: (0, -1),
        pg.K_s: (0, 1),
        pg.K_a: (-1, 0),
        pg.K_d: (1, 0),
    }

    # スプライトの更新
    for ship in ships:
        if ship.ship_num == 1:
            ship.update(key_states, ship1_controls, screen)
        elif ship.ship_num == 2:
            ship.update(key_states, ship2_controls, screen)

    # 定期的に燃料スプライトを追加
    if tmr % 300 == 0: 
        fuel = Fuel()
        fuels.add(fuel)

    bullets.update()
    lightnings.update()
    explosion2s.update()
    explosions.update()
    fuels.update()
    birds.update()
    hp_bar1.update()
    hp_bar2.update()

    # 衝突および相互作用をチェック
    handle_collisions(ships, bullets, lightnings, explosion2s, explosions,
                      fuels, tmr, hp_bar1, hp_bar2, fuel_bar1, fuel_bar2)

    # 点滅の更新
    if ship1.alive():
        ship1_blink.update(screen)
    if ship2.alive():
        ship2_blink.update(screen)

    # アニメーションが完了した場合はライトニングを削除
    for lightning in list(lightnings):
        if lightning.animation_done:
            lightnings.remove(lightning)

    # アニメーションが完了した場合は爆発2を削除
    for explosion in list(explosion2s):
        if explosion.animation_done:
            explosion2s.remove(explosion)

    # どちらかのプレイヤーが「死亡」したか確認
    if hp_bar1.hp <= 0 or hp_bar2.hp <= 0:
        if hp_bar1.hp <= 0 and ship1.alive():
            ship1.kill()
        if hp_bar2.hp <= 0 and ship2.alive():
            ship2.kill()
        return True  # ゲーム終了を示す

    return False


def draw_game_state(screen, ships, bullets, lightnings, explosions, explosion2s, birds, fuels, hp_bar1, hp_bar2, ship1_shield, ship2_shield, key_states, fuel_bar1, fuel_bar2):
    """
    ゲームの現在の状態を画面に描画します。
    """
    # スプライトの描画
    ships.draw(screen)
    bullets.draw(screen)
    lightnings.draw(screen)
    explosion2s.draw(screen)
    explosions.draw(screen)
    birds.draw(screen)
    fuels.draw(screen)
    # UI要素の描画
    hp_bar1.draw(screen)
    hp_bar2.draw(screen)
    fuel_bar1.draw(screen)
    fuel_bar2.draw(screen)

    # プレイヤー1が生きており、かつEnterキーが押されている場合にシールドを表示
    for ship in ships:
        if ship.ship_num == 1 and ship.alive() and key_states[pg.K_RETURN]:
            if fuel_bar1.fuel > 0:
                ship1_shield.update(screen)
                screen.blit(ship1_shield.image, ship1_shield.rect)
                fuel_bar1.decrease(0.5)

    # プレイヤー2が生きており、かつTabキーが押されている場合にシールドを表示
    for ship in ships:
        if ship.ship_num == 2 and ship.alive() and key_states[pg.K_TAB]:
            if fuel_bar2.fuel > 0:
                ship2_shield.update(screen)
                screen.blit(ship2_shield.image, ship2_shield.rect)
                fuel_bar2.decrease(0.5)


def display_end_game_result(screen, hp_bar1, hp_bar2):
    """
    ゲーム終了時の結果を画面に表示します。
    """
    # フォントの設定
    font = pg.font.Font(None, 74)  
    
    # プレイヤー1が負けた場合
    if hp_bar1.hp <= 0:
        text = font.render("Player 2 Wins!", True, (255, 0, 0))
    # プレイヤー2が負けた場合
    elif hp_bar2.hp <= 0:
        text = font.render("Player 1 Wins!", True, (0, 255, 0))

    # テキストを画面に描画
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    pg.display.flip()  



if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()


if __name__ == "__main__":

    pg.init()
    main()
    pg.quit()
    sys.exit()
