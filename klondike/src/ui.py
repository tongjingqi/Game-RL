from pygame import Color, sprite, image
import pygame
from input import InputManager

class Button(sprite.Sprite):
    """
    base button class
    """

    def __init__(self, img, down_img, pos, func, *args):
        super().__init__()
        
        self.image = img

        self.up_image = img
        self.hovered_image = img.copy()
        self.down_image = down_img
 
        self.hover_color = Color(15,15,15,255)

        self.rect = img.get_rect()
        self.rect.x = pos.x
        self.rect.y = pos.y

        self.func = func
        self.func_args = args

        self.hovered = False
        self.down = False

    def update(self):
        if InputManager.MOUSE_LEFT_UP() or not InputManager.MOUSE_LEFT():
            self.image = self.up_image
            self.down = False

        if self.rect.collidepoint(InputManager.cursor_pos):
            if InputManager.MOUSE_LEFT_DOWN():
                self.on_click()
            else:
                if not self.down: 
                    self.on_hover()
        else:
            if self.hovered and not self.down:
                print("unhovered")
                self.image = self.up_image
                self.image.fill(self.hover_color, special_flags=pygame.BLEND_SUB)
                self.hovered = False

    def on_hover(self):
        if not self.hovered:
            print("hovered")
            self.image.fill(self.hover_color, special_flags=pygame.BLEND_ADD)
            self.hovered = True

    def on_click(self):
        self.func(*self.func_args)
        if not self.down:
            self.down = True
            self.image = self.down_image

class UIAssets():
    def __init__(self):

        self.reset_button = image.load("assets/button_reset.png").convert_alpha()
        self.reset_button_down = image.load("assets/button_reset_down.png").convert_alpha()

