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
    def __init__(self, center, size=(100, 100)):
        super().__init__()
        self.images = []
        self.load_images()
        self.current_frame = 0
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect(center=center)
        self.frame_count = 0
        self.animation_speed = 1
        # Total frames for the explosion animation
        self.total_frames = 10 * 5  # Number of images times desired frames per image

    def load_images(self):
        for i in range(1, 11):  # Assuming you have 10 images for the explosion
            img = pg.image.load(
                f'{MAIN_DIR}/fig/Explosion_{i}.png').convert_alpha()
            img = pg.transform.scale(img, (100, 100))  # Scale to desired size
            self.images.append(img)

    def update(self):
        if self.frame_count < self.total_frames or self.current_frame < len(self.images) - 1:
            self.current_frame = (self.frame_count // 5) % len(self.images)
            self.image = self.images[int(self.current_frame)]
            self.frame_count += 1
        else:
            self.kill()  # Kill the sprite after the animation


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


class AnimatedShield(pg.sprite.Sprite):
    def __init__(self, ship: Ship, image_path, frame_count, new_size=None):
        super().__init__()
        self.ship = ship
        self.spritesheet = pg.image.load(image_path).convert_alpha()
        self.frame_count = frame_count
        self.frames = self.load_frames(self.frame_count, new_size)
        self.current_frame = 0
        self.animation_speed = 0.2
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=self.ship.rect.center)

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

    def update(self):
        self.animate()
        self.rect = self.image.get_rect(center=self.ship.rect.center)

class Bullet1(pg.sprite.Sprite):#wasdプレイヤーの爆弾
    def __init__(self,ship: Ship):
        super().__init__()
        self.vx, self.vy = (0,+1)#下方向に
        self.image = pg.image.load(f"{MAIN_DIR}/fig/6.png")#ドーナツを挿入
        self.rect = self.image.get_rect()
        self.rect.centerx = ship.rect.centerx
        self.rect.centery = ship.rect.bottom
        self.speed = 10#爆弾の速度
    
    def update(self):
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)

class Bullet2(pg.sprite.Sprite):#矢印プレイヤーの爆弾
    def __init__(self,ship: Ship):
        super().__init__()
        self.vx, self.vy = (0,-1)#上方向に
        self.image = pg.image.load(f"{MAIN_DIR}/fig/6.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = ship.rect.centerx
        self.rect.centery = ship.rect.top
        self.speed = 10#爆弾の速度
    
    def update(self):
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
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
        # Position the lightning at the bottom of the ship
        self.rect.centerx = ship.rect.centerx
        self.rect.bottom = ship.rect.top  # Align the top of the lightning with the bottom of the ship
        self.animation_done = False
        self.hit = False
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

        self.effect_bar = Rect(self.x + 4+self.label.get_width(),self.y+2,self.width -4, self.label.get_height()-4)
        self.effect_color = (0,255,255)

    def update(self):
        if self.hp >= self.max:
            self.hp = self.max

        if self.effect_bar.width > self.mark * self.hp:
            self.value.width = self.mark * self.hp
            if self.effect_bar.width >= self.value.width:
                self.effect_bar.width = self.mark * self.hp
        elif self.value.width < self.mark * self.hp:
            self.effect_bar.width = self.mark * self.hp
            self.value.inflate_ip(1,0)

        if self.effect_bar.width <= self.bar.width /6:
            self.effect_color - (255,255,0)
        elif self.effect_color <= self.bat.width /2:
            self.effect_color = (255,255,0)
        else:
            self.effct_color = (0,255,0)

    
    def draw(self,screen):
        pg.draw.rect(screen,(255,255,255),self.frame)
        pg.draw.rect(screen,(0,0,0),self.bar)
        pg.draw.rect(screen,self.effect_color,self.effect_bar)
        pg.draw.rect(screen, (0,0,255),self.value)
        screen.blit(self.label,(self.x,self.y))


def main():
    bird_image_path = os.path.join(MAIN_DIR, 'fig/Walk.png')
    birds = pg.sprite.Group()
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    score = Score()
    score2 = Scores()
    fuels = pg.sprite.Group()

    hp_bar1 = HealthBar(10,10,100,12)
    hp_bar2 = HealthBar(1200,500,100,12)
    bg_img_original = pg.image.load(f"{MAIN_DIR}/imgs/bg_ocean.png")
    bg_img = pg.transform.scale(bg_img_original, (WIDTH, HEIGHT))
    bg_img_flipped = pg.transform.flip(bg_img, True, False)
    bg_x = 0
    bg_x_flipped = bg_img.get_width()
    bg_tile_width = bg_img.get_width()
    bg_tile_height = bg_img.get_height()
    explosion2s = pg.sprite.Group()
    # Calculate how many tiles are needed to cover the screen
    tiles_x = -(-WIDTH // bg_tile_width)  # Ceiling division
    tiles_y = -(-HEIGHT // bg_tile_height)  # Ceiling division
    new_ship_size = (40, 40)
    ship1_frame_count = 8  # Update this if your sprite sheet has a different number of frames
    ship2_frame_count = 4  # Update this if your sprite sheet has a different number of frames
    ship1_frame_count_idle = 10  # Replace with the number of idle frames for ship1
    ship1_frame_count_move = 10  # Replace with the number of move frames for ship1
    ship1 = Ship(1, (100, 200), ship1_frame_count_idle,
                 ship1_frame_count_move, ship_num=1, new_size=(150, 150))

    ship2_frame_count_idle = 10  # Replace with the number of idle frames for ship2
    ship2_frame_count_move = 10  # Replace with the number of move frames for ship2
    ship2 = Ship(2, (1000, 500), ship2_frame_count_idle,
                 ship2_frame_count_move, ship_num=2, new_size=(150, 150))

    ships = pg.sprite.Group(ship1, ship2)

    ship1_controls = {
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (1, 0),
    }
    ship2_controls = {
        pg.K_w: (0, -1),
        pg.K_s: (0, +1),
        pg.K_a: (-1, 0),
        pg.K_d: (1, 0),
    }
    bullets = pg.sprite.Group()
    
    for _ in range(5):  # 鳥数が５に
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        # スピードをランダムに
        speed_x = random.choice([1, 2, 3])
        speed_y = random.choice([-3, -2, -1, 1, 2, 3])
        bird = Bird(bird_image_path, (x, y), frame_count=6,
                    speed=(speed_x, speed_y))
        birds.add(bird)

    shield1_sprite_path = os.path.join(MAIN_DIR, 'fig/shield1.png')
    shield1_frame_count = 8  # The number of frames in the shield1 sprite sheet
    shield2_sprite_path = os.path.join(MAIN_DIR, 'fig/shield2.png')
    shield2_frame_count = 7  # The number of frames in the shield2 sprite sheet

    # Example size, adjust this to your preference
    new_shield_size = (200, 200)

    ship1_shield = AnimatedShield(
        ship1, shield1_sprite_path, shield1_frame_count, new_size=(300, 300))
    ship2_shield = AnimatedShield(
        ship2, shield2_sprite_path, shield2_frame_count, new_size=(280, 280))
    # Update with your blink sprite sheet file name
    blink_image_path = os.path.join(MAIN_DIR, 'fig/blink.png')
    blink_frame_count = 8  # Update with the correct number of frames

    ship1_blink = Blink(ship1, blink_image_path, blink_frame_count)
    ship2_blink = Blink(ship2, blink_image_path, blink_frame_count)
    ship1.blink_instance = ship1_blink
    ship2.blink_instance = ship2_blink

    explosion1 = Explosion(center=ship1.rect.center)
    explosion2 = Explosion(center=ship2.rect.center)

    lightnings = pg.sprite.Group()
    explosions = pg.sprite.Group()
    tmr = 0
    clock = pg.time.Clock()

    while True:
        bg_x -= 1
        bg_x_flipped -= 1
        ships.draw(screen)
        # イベントハンドラー
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_RIGHTBRACKET:
                bullets.add(Bullet1(ship1))
            if event.type == pg.KEYDOWN and event.key == pg.K_g:
                bullets.add(Bullet2(ship2))
            if event.type == pg.KEYDOWN and event.key == pg.K_LEFTBRACKET:
                lightnings.add(Lightning1(ship1))
            if event.type == pg.KEYDOWN and event.key == pg.K_h:
                lightnings.add(Lightning2(ship2))

         #燃料と船が接触したかの判定
        for fuel in fuels:
                if ship1.rect.colliderect(fuel.rect):
                    score.score += 20
                    fuel.kill()
                if ship2.rect.colliderect(fuel.rect):
                    score2.scores += 20
                    fuel.kill()
        # 300フレームに1回，燃料を出現させる
        if tmr % 300 == 0:
            fuels.add(Fuel())
     
        # 背景をブリット
        for lightning in lightnings:
            if ship1.rect.colliderect(lightning.rect):
                explosion2s.add(Explosion2(ship1.rect.center))  # Create an explosion at ship2's location
                ex = tmr
                if ex == tmr + 2:
                    lightnings.remove(lightning)
            if ship2.rect.colliderect(lightning.rect):
                explosion2s.add(Explosion2(ship2.rect.center))  # Create an explosion at ship2's location
                ex = tmr
                if ex == tmr + 2:
                    lightnings.remove(lightning)
        screen.blit(bg_img, [0, 0])
         # 背景をブリット

        for y in range(tiles_y):
            for x in range(tiles_x):
                screen.blit(bg_img, (x * bg_tile_width, y * bg_tile_height))
        if bg_x < -bg_img.get_width():
            bg_x = bg_img.get_width()
        if bg_x_flipped < -bg_img.get_width():
            bg_x_flipped = bg_img.get_width()
        screen.blit(bg_img, (bg_x, 0))
        screen.blit(bg_img_flipped, (bg_x_flipped, 0))

        if key_lst[pg.K_LSHIFT]:
            direction = (-1, 0) if key_lst[pg.K_a] else (1, 0)
            if not ship2.blinking:
                ship2_blink.start_blink(direction)

        if key_lst[pg.K_RSHIFT]:
            direction = (-1, 0) if key_lst[pg.K_LEFT] else (1, 0)
            if not ship1.blinking:
                ship1_blink.start_blink(direction)

        # Inside the game loop
        collision = pg.sprite.collide_rect(ship1, ship2)
        for explosion in explosions:
            explosion.update()
            screen.blit(explosion.image, explosion.rect)

        if collision:
            # Add the explosions to the explosions group
            explosions.add(explosion1, explosion2)
            explosions.update()

            explosion1.rect.center = ship1.rect.center
            explosion2.rect.center = ship2.rect.center
            # Kill both ships to remove them from the game
            ship1.kill()
            ship2.kill()

        explosions.update()
        ship1_blink.update(screen)
        ship2_blink.update(screen)
        birds.update()  # 鳥をアップデート
        birds.draw(screen)
        if ship1.alive():
            ship1.update(key_lst, ship1_controls, screen)
        if ship2.alive():
            ship2.update(key_lst, ship2_controls, screen)
        for ship in ships:
            if ship.alive():
                screen.blit(ship.image, ship.rect)
            else:
                ship.kill()
        if ship1.alive():
            if key_lst[pg.K_RETURN]:
                ship1_shield.update()
                screen.blit(ship1_shield.image, ship1_shield.rect)

        if ship2.alive():
            if key_lst[pg.K_TAB]:
                ship2_shield.update()
                screen.blit(ship2_shield.image, ship2_shield.rect)
        explosions.draw(screen)
        bullets.update()
        bullets.draw(screen)
        lightnings.update()
        lightnings.draw(screen)
        explosion2s.update()
        explosion2s.draw(screen)
        for lightning in list(lightnings):
            if lightning.animation_done:
                lightnings.remove(lightning)
        explosions.draw(screen)
        for explosion in list(explosion2s):
            if explosion.animation_done:
                explosion2s.remove(explosion)
        hp_bar1.draw(screen)
        hp_bar2.draw(screen)
        score.update(screen)
        score2.update(screen)
        fuels.draw(screen)

        pg.display.update()
        tmr += 1
        clock.tick(50)
#

if __name__ == "__main__":

    pg.init()
    main()
    pg.quit()
    sys.exit()
    