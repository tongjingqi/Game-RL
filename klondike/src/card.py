from pygame import transform
from pygame import sprite 
from pygame import image

from pygame import Surface
from pygame import Rect

from enum import Enum

import pygame

class Rank(Enum):
    ACE =   1
    TWO =   2
    THREE = 3
    FOUR =  4
    FIVE =  5
    SIX =   6
    SEVEN = 7
    EIGHT = 8
    NINE =  9
    TEN =   10
    JACK =  11
    QUEEN = 12
    KING =  13

str_to_rank = {'A': Rank.ACE, 
               2: Rank.TWO, 
               3: Rank.THREE, 
               4: Rank.FOUR, 
               5: Rank.FIVE, 
               6: Rank.SIX, 
               7: Rank.SEVEN, 
               8: Rank.EIGHT, 
               9: Rank.NINE, 
               10: Rank.TEN, 
               'J': Rank.JACK, 
               'Q': Rank.QUEEN, 
               'K': Rank.KING}

class Card(sprite.Sprite):
    def __init__(self, img, back_img, rank, suit):
        super().__init__()

        self.image = back_img

        self.front = img
        self.rect = img.get_rect()

        self.color = "blue" if suit == "spade" or suit == "club" else "red"
        self.rank: Rank = str_to_rank[rank]
        self.suit = suit

        self.selected = False
        self.faceup = False
        
    def flip_up(self):
        self.image = self.front
        self.faceup = True

    def flip_back(self, back_img):
        self.image = back_img
        self.faceup = False
 

class CardAssets:
    def __init__(self):
                
        suits = ["heart", "spade", "diamond", "club"]

        self.letters = self.load_letters()
        self.numbers = self.load_nums()

        self.card_front = image.load(
            "assets/card_front.png").convert_alpha()

        self.card_back = image.load(
            "assets/card_back.png").convert_alpha()

        self.big_suits = {
            suit: image.load(
                "assets/big_" + suit + ".png").convert_alpha() 
            for suit in suits
        }

        self.small_suits = {
            suit: image.load(
                "assets/small_" + suit + ".png").convert_alpha() 
            for suit in suits
        }

        colors = ["red", "blue"]
        faces = ['J', 'Q', 'K']

        self.faces = {
            color: {
                face: image.load(
                    "assets/" + color + "_" + face + ".png").convert_alpha() 
                for face in faces
            } 
            for color in colors
        }

    
    def get_cards(self, ranks, suits, scale) -> dict[str, dict[str, Card]]:
        cards = {
            rank: {
                suit: self.composite_card((rank, suit), scale)
                for suit in suits
            } 
            for rank in ranks
        }

        return cards


    def load_letters(self) -> dict[str, Surface]:
        l = image.load("assets/letters.png").convert_alpha()
        
        symbol_w = 5
        symbol_rect = Rect(0, 0, symbol_w, 8)

        lets = ['A', 'K', 'Q', 'J']
        letters = {}

        for i, char in enumerate(lets):
            symbol_rect.x = symbol_w * i
            sub = l.subsurface(symbol_rect)
            letters[char] = sub

        return letters

    def load_nums(self) -> dict[int, Surface]:
        l = image.load("assets/numbers.png").convert_alpha()
        
        symbol_w = 5
        symbol_rect = Rect(0, 0, symbol_w, 8)

        nums = [9, 8, 7, 6, 5, 4, 3, 2, 10]
        numbers = {}

        for i, num in enumerate(nums):
            if num == 10:
                symbol_rect.w = 8
            symbol_rect.x = symbol_w * i
            sub = l.subsurface(symbol_rect)
            numbers[num] = sub

        return numbers


    def blit_suits_num(self, rank, suit, suit_surface: Surface, card_surface: Surface):
        card_w = card_surface.get_width()
        card_h = card_surface.get_height()
        
        b_w = suit_surface.get_width()
        b_h = suit_surface.get_height()

        x = 13
        y = 9

        rot_suit_surface: Surface = transform.rotate(suit_surface, 180)
        
        if rank % 2 == 1 and rank != 7:
            blit_x = card_w // 2 - b_w // 2
            blit_y = card_h // 2 - b_h // 2
            if suit == "heart":
                blit_y = blit_y + 1
            else:
                blit_y = blit_y - 1

            card_surface.blit(suit_surface, 
                              (blit_x, blit_y))
            
        if rank == 2 or rank == 3:
            blit_x = card_w // 2 - b_w // 2
            blit_y = y
            card_surface.blit(suit_surface, 
                              (blit_x, blit_y))
            blit_y = card_h - blit_y - b_h
            card_surface.blit(rot_suit_surface, 
                              (blit_x, blit_y))

        if rank >= 4:
            blit_x = x
            blit_y = y
            # upper left
            card_surface.blit(suit_surface, 
                              (blit_x, blit_y))
            blit_x = card_w - x - b_w
            # upper right
            card_surface.blit(suit_surface, 
                              (blit_x, blit_y))

            blit_x = x
            blit_y = card_h - y - b_h
            # bot left
            card_surface.blit(rot_suit_surface, 
                              (blit_x, blit_y))

            blit_x = card_w - x - b_w
            #bot right
            card_surface.blit(rot_suit_surface, 
                              (blit_x, blit_y))

        if rank == 6 or rank == 7:
            blit_x = x
            blit_y = card_h // 2 - b_h // 2
            if suit == "heart":
                blit_y = blit_y + 1
            else:
                blit_y = blit_y - 1

            # mid left
            card_surface.blit(suit_surface, 
                              (blit_x, blit_y))

            blit_x = card_w - x - b_w
            # mid right
            card_surface.blit(suit_surface, 
                              (blit_x, blit_y))

        if rank >= 8:
            blit_x = x
            blit_y = card_h // 2 - b_h - 2
            # left up
            card_surface.blit(suit_surface, 
                              (blit_x, blit_y))
            
            blit_x = card_w - x - b_w
            # right up
            card_surface.blit(suit_surface, 
                              (blit_x, blit_y))

            blit_x = x
            blit_y = card_h // 2 + 2
            # left down
            card_surface.blit(rot_suit_surface, 
                              (blit_x, blit_y))

            blit_x = card_w - x - b_w
            # right down
            card_surface.blit(rot_suit_surface, 
                              (blit_x, blit_y))

        if rank == 7:
            blit_x = card_w // 2 - b_w // 2
            blit_y = card_h // 4
            # upper mid
            card_surface.blit(suit_surface, 
                              (blit_x, blit_y))

        if rank == 10:
            blit_x = card_w // 2 - b_w // 2
            blit_y = card_h // 4 - b_h // 4
            # upper mid
            card_surface.blit(suit_surface, 
                              (blit_x, blit_y))
            
            blit_y = card_h - blit_y - b_h
            # bottom mid
            card_surface.blit(rot_suit_surface, 
                              (blit_x, blit_y))

    def composite_card(self, c: tuple, scale) -> Card:
        rank = c[0]
        suit = c[1]

        suit_b: Surface = self.big_suits[suit].copy()
        b_w = suit_b.get_width()
        b_h = suit_b.get_height()

        suit_s: Surface = self.small_suits[suit].copy()
        s_w = suit_s.get_width()

        card = self.card_front.copy()
        card_w = card.get_width()
        card_h = card.get_height()

        color = suit_b.get_at((b_w // 2, b_h // 2))

        # get the symbol and set its color to the suit
        if type(rank) is int:
            symbol: Surface = self.numbers[rank].copy()

            # blit the suits onto the card surface
            self.blit_suits_num(rank, suit, suit_b, card)
            
        else:
            symbol: Surface = self.letters[rank].copy()
            if rank == 'A':
                self.blit_suits_num(1, suit, suit_b, card)
            else:
                x = card_w // 2
                y = card_h // 2

                if suit == "heart" or suit == "diamond":
                    surf = self.faces["red"][rank]
                else:
                    surf = self.faces["blue"][rank]

                x = x - surf.get_width() // 2
                y = y - surf.get_height() // 2

                card.blit(surf, 
                          (x, y))

        """
        place the numbers in the upper left and bottom right of the card
        """
        sym_w = symbol.get_width()
        sym_h = symbol.get_height()

        symbol.fill(color, special_flags=pygame.BLEND_MIN)

        up_l_x = 4
        up_l_y = 3

        v_line_l = 6
        v_line_r = card_w - v_line_l - 1
        v_small_suit_offset = sym_h + up_l_y + 1

        if rank == 10:
            up_l_x = 3

        low_r_x = card_w - up_l_x - sym_w
        low_r_y = card_h - up_l_y - sym_h

        card.blit(symbol, 
                  (up_l_x, up_l_y))

        flip_sym = transform.rotate(symbol, 180)

        card.blit(flip_sym, 
                  (low_r_x, low_r_y))

        card.blit(suit_s, 
                  (v_line_l - (s_w // 2), 
                   v_small_suit_offset))

        flip_suit = transform.rotate(suit_s, 180)

        card.blit(flip_suit, 
                  (v_line_r - (s_w // 2), 
                   card_h - sym_h - v_small_suit_offset - 2))

        card = transform.scale_by(card, scale)
        back = transform.scale_by(self.card_back, scale)
        return Card(card, back, rank, suit)

       
