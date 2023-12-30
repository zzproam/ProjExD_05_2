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
    1: 'Idle1.png',  # The path to the idle image for ship1
    2: 'Idle2.png'   # The path to the idle image for ship2
}
move_image_paths = {
    1: 'Move1.png',  # The path to the move image for ship1
    2: 'Move2.png'   # The path to the move image for ship2
}


def restrict_ship_movement(ship, ship_num):
    # 異なる船の境界を定義する辞書
    ship_bounds = {
        1: (0, 0, WIDTH, 400),   # 船1の境界：(左、上、右、下)
        2: (0, 500, WIDTH, HEIGHT)  # 船2の境界：(左、上、右、下)
    }

    # ship_numに基づいて船の境界を取得；見つからない場合はデフォルト値を使用
    min_x, min_y, max_x, max_y = ship_bounds.get(ship_num, (0, 0, WIDTH, HEIGHT))

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
    def __init__(self, ship: Ship, image_path, frame_count):
        super().__init__()
        self.ship = ship
        self.spritesheet = pg.image.load(image_path).convert_alpha()
        self.frame_count = frame_count
        self.frames = self.load_frames(self.frame_count)
        self.current_frame = 0
        self.animation_speed = 1
        self.active = False  # Indicates if the blink is active

    def animate(self):
        if self.active:
            self.current_frame += self.animation_speed
            if self.current_frame >= len(self.frames):
                self.current_frame = 0
            self.image = self.frames[int(self.current_frame)]
            self.rect = self.image.get_rect(center=self.ship.rect.center)

    def start_blink(self, direction):
        self.active = True
        self.ship.blinking = True  # Tell the ship it's blinking
        self.ship.blink_direction = direction
        self.current_frame = 0  # Reset animation frame

        # Flip the animation frames if the blink direction is to the left
        self.frames = [pg.transform.flip(
            frame, True, False) if direction[0] < 0 else frame for frame in self.original_frames]

    def stop_blink(self):
        self.active = False
        self.ship.blinking = False  # Tell the ship it's done blinking

    def load_frames(self, frame_count):
        # Split the spritesheet into frames and resize if new_size is provided.
        frames = []
        frame_width = self.spritesheet.get_width() // frame_count
        frame_height = self.spritesheet.get_height()
        for i in range(frame_count):
            frame = self.spritesheet.subsurface(
                (i * frame_width, 0, frame_width, frame_height))
            frame = pg.transform.rotozoom(frame, 225, 1.0)
            frames.append(frame)
        # Store the original frames for flipping
        self.original_frames = list(frames)
        return frames

    def update(self, screen: pg.Surface):
        self.animate()
        if self.active:
            # Position the animation on the edge of the ship's rect based on direction
            if self.ship.blink_direction[0] > 0:  # If moving left
                self.rect.right = self.ship.rect.left
            else:  # If moving right
                self.rect.left = self.ship.rect.right
            screen.blit(self.image, self.rect)


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
    def __init__(self, num: int, xy: tuple[int, int], idle_frames, move_frames, ship_num, new_size):
        super().__init__()
        self.idle_images = self.load_images(
            f"{MAIN_DIR}/fig/Idle{num}.png", idle_frames, new_size)
        self.move_images = self.load_images(
            f"{MAIN_DIR}/fig/Move{num}.png", move_frames, new_size)
        self.images = self.idle_images  # Start with idle images
        self.current_frame = 0
        self.animation_speed = 0.2
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect(center=xy)
        self.speed = 10
        self.moving = False  # Indicates whether the ship is moving
        self.moving_left = False  # Indicates whether the ship is moving to the right

        self.blinking = False
        self.blink_distance = 500  # Updated blink distance
        self.blink_direction = (1, 0)  # Default blink direction to the right

        self.last_direction = (+1, 0)

        self.blink_speed = 20  # How fast the ship blinks per frame

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
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.images):
            self.current_frame = 0
        self.image = self.images[int(self.current_frame)]
        if self.moving and self.moving_left:
            self.image = pg.transform.flip(self.image, True, False)

    def update(self, key_lst: list[bool], ctrl_keys: dict, screen: pg.Surface):
        self.moving = False  # Reset moving state
        sum_mv = [0, 0]
        if not self.blinking:
            for k, mv in ctrl_keys.items():
                if key_lst[k]:
                    self.rect.move_ip(+self.speed*mv[0], +self.speed*mv[1])
                    sum_mv[0] += mv[0]
                    sum_mv[1] += mv[1]
                    self.moving = True
                    self.moving_left = mv[0] < 0
                if sum_mv != [0, 0]:
                    # Update the last direction when moving
                    self.last_direction = (sum_mv[0], sum_mv[1])
        else:
            # Blinking movement code
            self.rect.x += self.blink_direction[0] * self.blink_speed
            self.blink_distance -= self.blink_speed
            if self.blink_distance <= 0:
                self.blinking = False
                self.blink_distance = 500  # Reset blink distance
                self.blink_direction = (1, 0)  # Reset blink direction
                # Trigger the stop_blink method of the Blink instance
                self.blink_instance.stop_blink()

        if self.moving:
            self.images = self.move_images
        else:
            self.images = self.idle_images
        restrict_ship_movement(self, self.ship_num)
        self.animate()
        screen.blit(self.image, self.rect)


class Shield(pg.sprite.Sprite):
    def __init__(self, ship: Ship, image_path=None, frame_count=0, new_size=None, radius=75, color=(0, 0, 255), width=2):
        super().__init__()
        self.ship = ship
        self.radius = radius
        self.color = color
        self.width = width
        self.is_animated = image_path is not None and frame_count > 0

        if self.is_animated:
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
        for i in range(frame_count):
            frame = self.spritesheet.subsurface(
                (i * frame_width, 0, frame_width, frame_height))
            if new_size:
                frame = pg.transform.scale(frame, new_size)
            frames.append(frame)
        return frames

    def animate(self):
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.frames):
            self.current_frame = 0
        self.image = self.frames[int(self.current_frame)]
        self.rect = self.image.get_rect(center=self.ship.rect.center)

    def update(self, screen: pg.Surface):
        if self.is_animated:
            self.animate()
            screen.blit(self.image, self.rect)
        else:
            pg.draw.circle(screen, self.color, self.ship.rect.center, self.radius, self.width)


class Bullet(pg.sprite.Sprite):
    def __init__(self, ship: Ship, direction: str):
        super().__init__()
        self.image = pg.image.load(f"{MAIN_DIR}/fig/6.png")
        self.rect = self.image.get_rect(center=(ship.rect.centerx,
                                                ship.rect.top if direction == "up" else ship.rect.bottom))
        self.speed = 10

        self.ship_num = ship.ship_num  # attribute to identify the ship that fired the bullet

        if direction == "up":
            self.vx, self.vy = (0, -1)
        elif direction == "down":
            self.vx, self.vy = (0, 1)
        else:
            raise ValueError("Invalid direction for bullet. Choose 'up' or 'down'.")

    def update(self):
        self.rect.move_ip(self.speed * self.vx, self.speed * self.vy)
        # Remove bullet if it goes off-screen
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()


class Lightning(pg.sprite.Sprite):
    def __init__(self, ship: Ship, direction: str):
        super().__init__()
        self.load_images(direction)  # Load images based on direction
        self.current_frame = 0
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect(centerx=ship.rect.centerx)

        # Set the initial position of the lightning
        if direction == "up":
            self.rect.bottom = ship.rect.top
        elif direction == "down":
            self.rect.top = ship.rect.bottom
        else:
            raise ValueError("Invalid direction for lightning. Choose 'up' or 'down'.")

        self.animation_done = False

    def load_images(self, direction):
        imgs = sorted([img for img in os.listdir(f"{MAIN_DIR}/Lightning")])
        self.images = []

        for img in imgs:
            image = pg.image.load(os.path.join(f"{MAIN_DIR}/Lightning", img)).convert_alpha()
            image = pg.transform.scale(image, (image.get_width() * 2, image.get_height() * 2))

            # Flip the image for upward direction
            if direction == "up":
                image = pg.transform.flip(image, False, True)

            self.images.append(image)

    def update(self):
        self.current_frame = (self.current_frame + 1) % len(self.images)
        self.image = self.images[self.current_frame]
        if self.current_frame == 0:
            self.animation_done = True


class Explosion2(pg.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.images = [pg.image.load(f"{MAIN_DIR}/Explosion_two_colors/Explosion_two_colors{frame}.png") for frame in range(1, 11)]
        self.current_frame = 0
        self.image = self.images[self.current_frame]  # Set the initial image
        self.rect = self.image.get_rect(center=position)
        self.animation_done = False

    def update(self):
        # Update the frame
        self.current_frame += 1
        if self.current_frame < len(self.images):
            self.image = self.images[self.current_frame]
        else:
            self.animation_done = True  # End the animation once all frames have been shown

            
class HealthBar():
    def __init__(self, x, y, width, max_hp):
        self.x = x
        self.y = y
        self.width = width
        self.max_hp = max_hp  # Set the maximum health to 100
        self.hp = max_hp
        self.mark = self.width / self.max_hp  # Calculate the width of each health point

        self.font = pg.font.Font(None, 32)
        self.label = self.font.render("HP", True, (255, 255, 255))
        self.frame = pg.Rect(self.x + 2 + self.label.get_width(), self.y, self.width, self.label.get_height())
        self.bar = pg.Rect(self.x + 4 + self.label.get_width(), self.y + 2, self.width - 4, self.label.get_height() - 4)
        self.value = pg.Rect(self.x + 4 + self.label.get_width(), self.y + 2, self.width - 4, self.label.get_height() - 4)
        self.effect_color = (0, 255, 0)  # Green color for the health bar

    def decrease(self, amount):
        self.hp = max(self.hp - amount, 0)
        self.value.width = self.mark * self.hp  # Update the width of the health bar

    def update(self):
        # Additional logic (if any) for updating the health bar
        pass

    def draw(self, screen):
        pg.draw.rect(screen, (255, 255, 255), self.frame)
        pg.draw.rect(screen, (0, 0, 0), self.bar)
        pg.draw.rect(screen, self.effect_color, self.value)
        screen.blit(self.label, (self.x, self.y))


def main():
    """
    この関数はゲームのメインループを含んでいます。画面の初期化、スプライトの作成、UI要素の設定、背景の初期化などのゲームの主要な部分がこの関数で実行されます。
    """
    screen = initialize_screen()
    birds, ships, bullets, lightnings, explosions, explosion2s, fuels, ship1, ship2, ship1_blink, ship2_blink, ship1_shield, ship2_shield= initialize_sprites()
    hp_bar1, hp_bar2, score, score2 = initialize_ui_elements()
    bg_img, bg_img_flipped, bg_x, bg_x_flipped, bg_tile_width, bg_tile_height, tiles_x, tiles_y = initialize_background()

    clock = pg.time.Clock()
    tmr = 0
    while True:
        handle_background_movement(bg_x, bg_x_flipped, bg_tile_width, bg_tile_height, tiles_x, tiles_y, screen, bg_img, bg_img_flipped)
        key_states = pg.key.get_pressed()  # Get the current state of the keyboard
        handle_events(pg.event.get(), key_states, ships, bullets, lightnings, ship1_blink, ship2_blink)

        update_game_state(ships, bullets, lightnings, explosion2s, explosions, fuels, birds, tmr, score, score2, ship1, ship2, ship1_blink, ship2_blink, key_states, screen, hp_bar1, hp_bar2)

        draw_game_state(screen, ships, bullets, lightnings, explosions, explosion2s, birds, fuels, hp_bar1, hp_bar2, score, score2, ship1_shield, ship2_shield, key_states)

        pg.display.update()
        tmr += 1
        clock.tick(50)
  

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
    birds = pg.sprite.Group()  #  鳥のスプライトを格納するグループ。
    for _ in range(5):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        speed_x = random.choice([1, 2, 3])
        speed_y = random.choice([-3, -2, -1, 1, 2, 3])
        bird = Bird(bird_image_path, (x, y), frame_count=6, speed=(speed_x, speed_y))
        birds.add(bird)

    ship1_frame_count_idle = 10  
    ship1_frame_count_move = 10  
    ship2_frame_count_idle = 10  
    ship2_frame_count_move = 10  

    # 2つの船のスプライト。
    ship1 = Ship(1, (100, 200), ship1_frame_count_idle, ship1_frame_count_move, ship_num=1, new_size=(150, 150))
    ship2 = Ship(2, (1000, 500), ship2_frame_count_idle, ship2_frame_count_move, ship_num=2, new_size=(150, 150))

    shield1_sprite_path = os.path.join(MAIN_DIR, 'fig/shield1.png')
    shield1_frame_count = 8  # The number of frames in the shield1 sprite sheet
    shield2_sprite_path = os.path.join(MAIN_DIR, 'fig/shield2.png')
    shield2_frame_count = 7  # The number of frames in the shield2 sprite sheet

    # Add these lines after creating ship1 and ship2 in initialize_sprites
    ship1_shield = Shield(ship1, shield1_sprite_path , shield1_frame_count, new_size=(300, 300))
    ship2_shield = Shield(ship2, shield2_sprite_path , shield2_frame_count, new_size=(300, 300))

    blink_frame_count_ship1 = 8  # Replace with the correct number of blink frames for ship1
    blink_frame_count_ship2 = 8  # Replace with the correct number of blink frames for ship2

    blink_image_path_ship1 = os.path.join(MAIN_DIR, 'fig/blink.png')  # Replace with the correct path
    blink_image_path_ship2 = os.path.join(MAIN_DIR, 'fig/blink.png')  # Replace with the correct path

    # Instantiate Blink objects
    ship1_blink = Blink(ship1, blink_image_path_ship1, blink_frame_count_ship1)
    ship2_blink = Blink(ship2, blink_image_path_ship2, blink_frame_count_ship2)
    # Assign Blink instances to Ships
    ship1.blink_instance = ship1_blink
    ship2.blink_instance = ship2_blink

    ships = pg.sprite.Group(ship1, ship2)
    bullets = pg.sprite.Group()
    lightnings = pg.sprite.Group()
    explosions = pg.sprite.Group()
    explosion2s = pg.sprite.Group()
    fuels = pg.sprite.Group()

    # Update the return statement to include these new instances
    return birds, ships, bullets, lightnings, explosions, explosion2s, fuels, ship1, ship2, ship1_blink, ship2_blink, ship1_shield, ship2_shield


def initialize_ui_elements():
    """
    UI要素(ヘルスバー、スコア表示)を初期化します。プレイヤー1のヘルスバーは画面の左上に、プレイヤー2のヘルスバーは画面の右上に表示されます。
    """
    # Player 1's health bar at the top-left corner
    hp_bar1 = HealthBar(10, 10, 100, 100)  # x, y, width, max

    # Player 2's health bar at the top-right corner
    # Adjust the x-coordinate to place it on the right (WIDTH - width of the bar - some margin)
    hp_bar2 = HealthBar(WIDTH - 200, 10, 100, 100)  # x, y, width, max

    score = Score()
    score2 = Scores()
    return hp_bar1, hp_bar2, score, score2


def initialize_background():
    """
    背景画像と関連設定を初期化します。
    """
    # Initialization code for background elements
    bg_img_original = pg.image.load(f"{MAIN_DIR}/imgs/bg_ocean.png")
    bg_img = pg.transform.scale(bg_img_original, (WIDTH, HEIGHT))
    bg_img_flipped = pg.transform.flip(bg_img, True, False)
    bg_x = 0
    bg_x_flipped = bg_img.get_width()
    bg_tile_width = bg_img.get_width()
    bg_tile_height = bg_img.get_height()
    tiles_x = -(-WIDTH // bg_tile_width)
    tiles_y = -(-HEIGHT // bg_tile_height)
    return bg_img, bg_img_flipped, bg_x, bg_x_flipped, bg_tile_width, bg_tile_height, tiles_x, tiles_y


def handle_background_movement(bg_x, bg_x_flipped, bg_tile_width, bg_tile_height, tiles_x, tiles_y, screen, bg_img, bg_img_flipped):
    """
    背景の動きを制御します。背景画像をスクロールさせることで、動いているように見せます。
    """
    bg_x -= 1
    bg_x_flipped -= 1

    if bg_x < -bg_tile_width:
        bg_x = bg_tile_width
    if bg_x_flipped < -bg_tile_width:
        bg_x_flipped = bg_tile_width

    for y in range(tiles_y):
        for x in range(tiles_x):
            screen.blit(bg_img, (x * bg_tile_width + bg_x, y * bg_tile_height))
            screen.blit(bg_img_flipped, (x * bg_tile_width + bg_x_flipped, y * bg_tile_height))

    return bg_x, bg_x_flipped


def handle_events(events, key_states, ships, bullets, lightnings, ship1_blink, ship2_blink):
    """
    キーボードやマウスなどのユーザー入力イベントを処理します。
    """
    # Retrieve ship1 and ship2 from the ships sprite group
    ship1 = next((ship for ship in ships if ship.ship_num == 1), None)
    ship2 = next((ship for ship in ships if ship.ship_num == 2), None)

    for event in events:
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            # add bullet for ship1
            if event.key == pg.K_RIGHTBRACKET:
                if ship1:
                    bullets.add(Bullet(ship1, "down"))
            # add bullet for ship2
            elif event.key == pg.K_g:
                if ship2:
                    bullets.add(Bullet(ship2, "up"))
            # add lightning for ship1         
            elif event.key == pg.K_LEFTBRACKET:
                lightnings.add(Lightning(ship1, "down"))
            # add lightning for ship2
            elif event.key == pg.K_h:
                lightnings.add(Lightning(ship2, "up"))
            # blinking for ship2
            elif event.key == pg.K_LSHIFT:
                direction = (-1, 0) if key_states[pg.K_a] else (1, 0)
                if not ship2.blinking:
                    ship2_blink.start_blink(direction)
            # blinking for ship1
            elif event.key == pg.K_RSHIFT:
                direction = (-1, 0) if key_states[pg.K_LEFT] else (1, 0)
                if not ship1.blinking:
                    ship1_blink.start_blink(direction)

            
def handle_collisions(ships, bullets, lightnings, explosion2s, explosions, fuels, tmr, score, score2, hp_bar1, hp_bar2):
    """
    スプライト間の衝突を検出し、それに応じた処理を行います。
    """
    # Retrieve ship1 and ship2 from the ships sprite group
    ship1 = next((ship for ship in ships if ship.ship_num == 1), None)
    ship2 = next((ship for ship in ships if ship.ship_num == 2), None)

    # ullet and ship Collision
    for bullet in list(bullets):
        if ship1 and bullet.rect.colliderect(ship1.rect) and bullet.ship_num != ship1.ship_num:
            explosions.add(Explosion(ship1.rect.center, size=(100, 100)))
            bullets.remove(bullet)
            hp_bar1.decrease(10)
        elif ship2 and bullet.rect.colliderect(ship2.rect) and bullet.ship_num != ship2.ship_num:
            explosions.add(Explosion(ship2.rect.center, size=(100, 100)))
            bullets.remove(bullet)
            hp_bar2.decrease(10)

    # lightning and ship Collision
    for lightning in lightnings:
        if ship1.rect.colliderect(lightning.rect):
            explosion2s.add(Explosion2(ship1.rect.center))  # Create an explosion at ship2's location
            ex = tmr
            hp_bar1.decrease(30)
            if ex == tmr + 2:
                lightnings.remove(lightning)

        if ship2.rect.colliderect(lightning.rect):
            explosion2s.add(Explosion2(ship2.rect.center))  # Create an explosion at ship2's location
            ex = tmr
            hp_bar2.decrease(30)
            if ex == tmr + 2:
                lightnings.remove(lightning)
        


def update_game_state(ships, bullets, lightnings, explosion2s, explosions, fuels, birds, tmr, score, score2, ship1, ship2, ship1_blink, ship2_blink, key_states, screen, hp_bar1, hp_bar2):
    """
    ゲームの状態を更新します。スプライトの移動、アニメーションの更新などが含まれます。
    """
    # Global definitions for ship controls
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

    # Update sprites
    for ship in ships:
        if ship.ship_num == 1:
            ship.update(key_states, ship1_controls, screen)
        elif ship.ship_num == 2:
            ship.update(key_states, ship2_controls, screen)

    bullets.update()
    lightnings.update()
    explosion2s.update()
    explosions.update()
    fuels.update()
    birds.update()
    hp_bar1.update()
    hp_bar2.update()

    # Check collisions and interactions
    handle_collisions(ships, bullets, lightnings, explosion2s, explosions, fuels, tmr, score, score2, hp_bar1, hp_bar2)   

    # Blinking updates
    if ship1.alive():
        ship1_blink.update(screen)
    if ship2.alive():
        ship2_blink.update(screen)

    # remove lightning if the animation is done
    for lightning in list(lightnings):
        if lightning.animation_done:
            lightnings.remove(lightning)

    # remove explosion2s if the animation is done
    for explosion in list(explosion2s):
        if explosion.animation_done:
             explosion2s.remove(explosion)
    
    

def draw_game_state(screen, ships, bullets, lightnings, explosions, explosion2s, birds, fuels, hp_bar1, hp_bar2, score, score2, ship1_shield, ship2_shield, key_states):
    """
    ゲームの現在の状態を画面に描画します。
    """
    # Draw all sprites
    ships.draw(screen)
    bullets.draw(screen)
    lightnings.draw(screen)
    explosion2s.draw(screen)
    explosions.draw(screen)
    birds.draw(screen)
    fuels.draw(screen)

    # Draw UI elements
    hp_bar1.draw(screen)
    hp_bar2.draw(screen)
    score.update(screen)
    score2.update(screen)

    # Access ship1 and ship2 from the ships group
    for ship in ships:
        if ship.ship_num == 1 and ship.alive() and key_states[pg.K_RETURN]:
            ship1_shield.update(screen)
            screen.blit(ship1_shield.image, ship1_shield.rect)
        elif ship.ship_num == 2 and ship.alive() and key_states[pg.K_TAB]:
            ship2_shield.update(screen)
            screen.blit(ship2_shield.image, ship2_shield.rect)
    

# Other necessary functions...

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
    


