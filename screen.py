import pygame as pg


class Screen():

    def __init__(self, name, width, height, img_source):
        self.name = name
        self.width = width
        self.height = height
        self.screen = pg.display.set_mode((self.width, self.height))
        self.bg_img = pg.image.load(img_source)

    def set_screen(self):
        pg.display.set_caption(self.name)

    def blit_screen(self):
        self.screen.blit(self.bg_img, [0, 0])


        


    





        