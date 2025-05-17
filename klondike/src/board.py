import random
from pygame import Rect, Vector2, sprite, transform
from card import Card, CardAssets, Rank
from input import InputManager
from ui import Button, UIAssets

import random
from pygame import Rect, Vector2, sprite, transform
from card import Card, CardAssets, Rank
from input import InputManager
from ui import Button, UIAssets

class Board:
    """
    main gameplay scene layout:
    |[draw][dump]      [pile][pile][pile][pile]
    |[tab0][tab1][tab2][tab3][tab4][tab5][tab6]
    |下面是代码对应
    |pile即是stack，tab即是tableau
    |下面是中文对应
    |[随机牌堆][未使用牌]  [已完成牌堆]
    |[下方堆叠牌堆]
    """
    
    #card_scale = 0.8
    card_offset = 5
    draw_pile_loc = Vector2((22 + card_offset) * 2, (16 + card_offset) * 2)
    dump_loc = Vector2(draw_pile_loc.x + 150 + 24, draw_pile_loc.y)

    reset_button_loc = Vector2(dump_loc.x + 212, dump_loc.y)

    stack_loc: list[Vector2] = [Vector2(((283 + 5) * 2 + (i * (75 + 12)) * 2), (16 + 5) * 2) for i in range(4)]

    tableau_loc: list[Vector2] = [Vector2((22 + 5 + (i * (75 + 12))) * 2, (130 + 5) * 2) for i in range(7)]

    def __init__(self):
        random.seed()

        self.ranks = ['A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']
        self.suits = ["heart", "spade", "diamond", "club"]

        self.deck = [(rank, suit) for rank in self.ranks for suit in self.suits]

        card_assets = CardAssets()
        
        self.card_back = transform.scale_by(card_assets.card_back, 2)
        self.cards = card_assets.get_cards(self.ranks, self.suits, 2)


        self.tableaux = [Tableau(pos) for pos in self.tableau_loc]
        self.stacks = [Stack(pos) for pos in self.stack_loc]

        self.selected_cards = []
        
        ui_assets = UIAssets()

        self.ui_elts = sprite.Group()
        self.ui_elts.add(
            Button(
                transform.scale_by(ui_assets.reset_button, 2), 
                transform.scale_by(ui_assets.reset_button_down, 2),
                self.reset_button_loc, 
                self.restart)
        )

        # Initialize draw pile and dump with proper positions but no cards yet
        self.draw_pile = DrawPile(pos=self.draw_pile_loc, back_img=self.card_back)
        self.dump = Dump(self.dump_loc)

        # Now decide which start method to use
        should_randomstart = random.choice([True, False])
        if should_randomstart:
            self.randomstart()
        else:
            random.shuffle(self.deck)  # Shuffle before normal setup
            self.setup()

    def randomstart(self):
        # 清空所有区域
        for tab in self.tableaux:
            tab.empty()
        for stack in self.stacks:
            stack.empty()
        self.draw_pile.empty()
        self.dump.empty()
        
        # 重新初始化牌组
        self.deck = [(rank, suit) for rank in self.ranks for suit in self.suits]
        random.shuffle(self.deck)
        
        # 填充基础堆，只能从A开始
        completed_stacks = random.randint(0, 2)
        used_suits = []
        for i in range(completed_stacks):
            stack = self.stacks[i]
            # 选择一个还没用过的花色
            available_suits = [suit for suit in self.suits if suit not in used_suits]
            if not available_suits:
                break
            
            suit = random.choice(available_suits)
            used_suits.append(suit)
            
            # 必须从A开始依次放入卡牌
            if ('A', suit) in self.deck:  # 确保有A可用
                for rank_idx in range(random.randint(1, 5)):  # 从A开始，最多到5
                    rank = self.ranks[rank_idx]
                    if (rank, suit) in self.deck:
                        card = self.cards[rank][suit]
                        card.flip_up()
                        stack.add(card)
                        self.deck.remove((rank, suit))
        
        # 填充tableau区域，每个tableau包含：
        # 1. 底部的隐藏牌（背面朝上）
        # 2. 顶部的可见序列（红黑交替且数字递减）
        for tableau in self.tableaux:
            # 第一部分：放置随机数量的隐藏牌
            hidden_count = random.randint(0, 4)  # 可以调整范围以控制难度
            if hidden_count > len(self.deck):  # 确保不会超出可用牌数
                hidden_count = len(self.deck)
                
            if hidden_count > 0:  # 只在需要隐藏牌时执行
                hidden_cards = random.sample(self.deck, hidden_count)
                for card_tuple in hidden_cards:
                    self.deck.remove(card_tuple)
                    card = self.cards[card_tuple[0]][card_tuple[1]]
                    card.flip_back(self.card_back)
                    tableau.add(card)

            # 第二部分：构造顶部可见序列
            if not self.deck:  # 检查是否还有可用的牌
                continue
                
            # 选择序列起始牌（只选择K-2，因为A没有后续牌）
            valid_start_ranks = [rank for rank in self.ranks[:-1] 
                                if any((rank, suit) in self.deck for suit in ["heart", "diamond", "spade", "club"])]
            
            if not valid_start_ranks:  # 如果没有合适的起始牌就跳过
                continue
                
            start_rank = random.choice(valid_start_ranks)
            # 从所有同点数的牌中随机选择一张作为起始牌
            valid_start_cards = [(start_rank, suit) for suit in ["heart", "diamond", "spade", "club"] 
                                if (start_rank, suit) in self.deck]
            start_tuple = random.choice(valid_start_cards)
            
            # 添加起始牌
            start_card = self.cards[start_tuple[0]][start_tuple[1]]
            start_card.flip_up()
            tableau.add(start_card)
            self.deck.remove(start_tuple)
            
            # 获取起始牌的属性
            current_rank_idx = self.ranks.index(start_tuple[0])
            current_color = "red" if start_tuple[1] in ["heart", "diamond"] else "black"

            # 构造递减序列
            while current_rank_idx > 0:  # 可以一直到A
                next_rank_idx = current_rank_idx - 1
                next_color = "red" if current_color == "black" else "black"
                next_suits = ["heart", "diamond"] if next_color == "red" else ["spade", "club"]
                
                # 找出所有符合条件的牌
                valid_cards = [(self.ranks[next_rank_idx], suit) 
                            for suit in next_suits 
                            if (self.ranks[next_rank_idx], suit) in self.deck]

                if not valid_cards:  # 没有合适的牌就结束序列
                    break

                # 随机选择一张合适的牌
                next_tuple = random.choice(valid_cards)
                next_card = self.cards[next_tuple[0]][next_tuple[1]]
                next_card.flip_up()
                tableau.add(next_card)
                self.deck.remove(next_tuple)

                current_rank_idx = next_rank_idx
                current_color = next_color

                # 随机决定是否继续序列（可以调整概率控制序列长度）
                if random.random() < 0.2:  # 20%概率结束序列
                    break

        # 将剩余的牌放入draw pile，都是背面朝上
        for rank, suit in self.deck:
            card = self.cards[rank][suit]
            card.flip_back(self.card_back)
            self.draw_pile.add(card)
        
        # 随机抽取一些牌到dump pile，这些牌是正面朝上的
        cards_to_dump = random.randint(0, min(3, len(self.draw_pile.sprites())))
        for _ in range(cards_to_dump):
            if self.draw_pile.sprites():
                card = self.draw_pile.get_top_sprite()
                card.flip_up()
                self.draw_pile.remove(card)
                self.dump.add(card)


    def restart(self):
        for tab in self.tableaux:
            tab.empty()

        for stack in self.stacks:
            stack.empty()

        self.draw_pile.empty()
        self.dump.empty()

        self.selected_cards = []

        self.deck = [(rank, suit) for rank in self.ranks for suit in self.suits]
        for r_n_a in self.deck:
            c = self.cards[r_n_a[0]][r_n_a[1]]
            if c.faceup:
                c.flip_back(self.card_back)

        random.shuffle(self.deck)
        self.setup()

    def get_card_from_deck(self):
        """Get a card from the deck, handling empty deck case."""
        if not self.deck:  # If deck is empty
            return None
        rank_and_suit = self.deck.pop(-1)
        rank = rank_and_suit[0]
        suit = rank_and_suit[1]
        card = self.cards[rank][suit]
        return card

    def setup(self):
        """Setup the initial game state, handling empty deck cases."""
        count = 1
        for tab in self.tableaux:
            for _ in range(count):
                card = self.get_card_from_deck()
                if card:  # Only add if we got a valid card
                    card.flip_back(self.card_back)  # Make sure cards are face down
                    tab.add(card)
                else:
                    print("Warning: Ran out of cards during tableau setup")
                    return  # Exit setup if we run out of cards
            
            # Flip the top card if there are any cards in this tableau
            if tab.sprites():
                tab.get_top_sprite().flip_up()
            count += 1

        # Initialize draw pile and dump
        self.draw_pile = DrawPile(pos=self.draw_pile_loc, back_img=self.card_back)
        self.dump = Dump(self.dump_loc)

        # Add remaining cards to draw pile
        while self.deck:
            card = self.get_card_from_deck()
            if card:
                card.flip_back(self.card_back)  # Make sure cards are face down
                self.draw_pile.add(card)

    def update(self):
        left_clicked = InputManager.MOUSE_LEFT_DOWN()
        left_lifted = InputManager.MOUSE_LEFT_UP()

        if left_lifted and self.selected_cards:
            if len(self.selected_cards) == 1:
                for stack in self.stacks:
                    if stack.drop(self.selected_cards[0]):
                        self.selected_cards = []
                        break

            if self.selected_cards:
                for tab in self.tableaux:
                    if tab.drop_stack(self.selected_cards):
                        self.selected_cards = []
                        break

            self.selected_cards = []

        self.ui_elts.update()

        for tab in self.tableaux:
            tab.update(self.selected_cards)

        for stack in self.stacks:
            stack.update(self.selected_cards)

        self.dump.update(self.selected_cards)
        self.draw_pile.update(self.dump)

        if left_clicked:
            for card in self.selected_cards:
                print(str(card.rank) + " " + str(card.rank.value))

    def draw(self, screen):
        self.draw_pile.draw(screen)
        self.dump.draw(screen)

        self.ui_elts.draw(screen)

        for tab in self.tableaux:
            tab.draw(screen)

        for stack in self.stacks:
            stack.draw(screen)

        for card in self.selected_cards:
            screen.blit(card.image, card.rect)

    def get_game_state_all_clear(self):
        """
        获取当前游戏状态，包括 draw、dump、pile、tableau 的卡牌情况。
        返回一个字典，方便序列化成 JSON。
        """
        return {
            "draw": [str(card.suit) + " " + str(card.rank.value) for card in self.draw_pile],
            "dump": [str(card.suit) + " " + str(card.rank.value) for card in self.dump],
            "piles": [[str(card.suit) + " " + str(card.rank.value) for card in pile] for pile in self.stacks],
            "tableau": [[str(card.suit) + " " + str(card.rank.value) for card in tableau] for tableau in self.tableaux]
        }

    def get_game_state(self):
        """
        获取当前游戏状态，包括 draw、dump、pile、tableau 的卡牌情况。
        返回一个字典，方便序列化成 JSON。
        仅显示正面朝上的卡牌内容，背面朝上的卡牌显示为 card 对象。
        """
        return {
            "draw": [str(card.suit) + " " + str(card.rank.value) if card.faceup else str(card) for card in self.draw_pile],
            "dump": [str(card.suit) + " " + str(card.rank.value) if card.faceup else str(card) for card in self.dump],
            "piles": [
                [str(card.suit) + " " + str(card.rank.value) if card.faceup else str(card) for card in pile] 
                for pile in self.stacks
            ],
            "tableau": [
                [str(card.suit) + " " + str(card.rank.value) if card.faceup else str(card) for card in tableau] 
                for tableau in self.tableaux
            ]
        }

        
class DrawPile(sprite.LayeredUpdates):
    def __init__(self, *sprites, pos: Vector2, back_img):
        super().__init__(*sprites)

        self.back = back_img
        self.pos = pos
        self.rect = Rect(pos.x, pos.y, 130, 180)

    def update(self, dump):
        if InputManager.MOUSE_LEFT_DOWN() \
            and self.rect.collidepoint(InputManager.cursor_pos):

            if self.sprites():
                self.draw_one(dump)
            else:
                self.reshuffle(dump)

    def add(self, *sprites, **kwargs):
        super().add(*sprites, **kwargs)

        for sprite in sprites:
            if type(sprite) == Card:
                sprite.rect.x = self.pos.x
                sprite.rect.y = self.pos.y


    def draw_one(self, dump):
        card = self.get_top_sprite()
        card.flip_up()

        self.remove(card)
        dump.add(card)

    def draw_cards(self, num):
        pass 

    def reshuffle(self, dump):
        cards = dump.sprites()
        for card in cards:
            card.flip_back(self.back)

        random.shuffle(cards)

        dump.empty()
        self.add(cards)

class Dump(sprite.LayeredUpdates):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.rect = Rect(pos.x, pos.y, 130, 180)
    
    def add(self, *sprites, **kwargs):
        super().add(*sprites, **kwargs)

        for sprite in sprites:
            if type(sprite) == Card:
                sprite.rect.x = self.pos.x
                sprite.rect.y = self.pos.y

    def update(self, selected_cards):
        super().update()

        cursor = InputManager.cursor_pos
        rel_cursor = InputManager.cursor_rel_pos

        left_clicked = InputManager.MOUSE_LEFT_DOWN()
        left_lifted = InputManager.MOUSE_LEFT_UP()

        sprites = self.sprites()

        x_offset = 1
        for i, card in enumerate(reversed(sprites[-1:-4:-1])):
            if not card.selected:
                card.rect.x = self.pos.x
                card.rect.x += x_offset * i
        
        if not sprites:
            return

        sprite = sprites[-1]

        if left_lifted and sprites[-1].selected:
            sprites[-1].selected = False
            sprites[-1].rect.x = self.pos.x
            sprites[-1].rect.y = self.pos.y
        elif sprites[-1].selected:
            sprites[-1].rect.x += rel_cursor[0]
            sprites[-1].rect.y += rel_cursor[1]

        if left_clicked and sprite.rect.collidepoint(cursor):
            selected_cards.append(sprites[-1])
            sprites[-1].selected = True

class Stack(sprite.LayeredUpdates):
    def __init__(self, pos):
        super().__init__()

        self.pos: Vector2 = pos
        self.rect = Rect(pos.x, pos.y, 130, 180)
        self.prev = 0

    def add(self, *sprite, **kwargs):
        super().add(*sprite, **kwargs)

        if sprite:
            sprite[0].rect.x = self.pos.x
            sprite[0].rect.y = self.pos.y

    def drop(self, card):
        cursor = InputManager.cursor_pos
        if self.rect.collidepoint(cursor):
            print("attempt to add to stack")
            if self.sprites():
                top = self.get_top_sprite()
                rank_val = top.rank.value
                suit = top.suit

                if card.rank.value == rank_val + 1 and card.suit == suit:
                    g = card.groups()[0]
                    g.remove(card)
                    if g.sprites():
                        g.get_top_sprite().flip_up()

                    self.add(card)
                    return True
                else:
                    print("wrong rank and or suit for populated stack")
                    print(card.rank)
                    print(card.suit)
                    return False
            else: 
                if card.rank == Rank.ACE:
                    g = card.groups()[0]
                    g.remove(card)
                    if g.sprites():
                        g.get_top_sprite().flip_up()

                    self.add(card)
                    return True
                else:
                    print("expected ace")
                    return False

        return False

    def update(self, selected_cards):

        cursor = InputManager.cursor_pos
        rel_cursor = InputManager.cursor_rel_pos

        left_clicked = InputManager.MOUSE_LEFT_DOWN()
        left_lifted = InputManager.MOUSE_LEFT_UP()


        sprites = self.sprites()
        
        if not sprites:
            return

        if left_lifted and sprites[-1].selected:
            sprites[-1].selected = False
            sprites[-1].rect.x = self.pos.x
            sprites[-1].rect.y = self.pos.y
        elif sprites[-1].selected:
            sprites[-1].rect.x += rel_cursor[0]
            sprites[-1].rect.y += rel_cursor[1]

        if left_clicked and self.rect.collidepoint(cursor):
            selected_cards.append(sprites[-1])
            sprites[-1].selected = True


        
class Tableau(sprite.LayeredUpdates):
    """
    tableaux are the 7 lower card piles
    maintain the following invariants:
        1. each face-up card must be 1 rank lower 
            than the face-up card below it
        2. each face-up card must be the opposite 
            color (red/blue) of the face-up card below it
    """

    def __init__(self, pos: Vector2):
        super().__init__()

        self.pos: Vector2 = pos
        self.rect = Rect(pos.x, pos.y, 130, 180)

    def update(self, selected_cards):
        super().update(InputManager.cursor_pos)

        cursor = InputManager.cursor_pos
        rel_cursor = InputManager.cursor_rel_pos

        left_clicked = InputManager.MOUSE_LEFT_DOWN()
        left_lifted = InputManager.MOUSE_LEFT_UP()


        y_offset = 0
        sprites = self.sprites()

        if left_lifted:
            for card in sprites:
                card.selected = False

        for card in sprites:
            if not card.selected:
                card.rect.x = self.pos.x
                card.rect.y = self.pos.y + y_offset
            else:
                card.rect.move_ip(rel_cursor)

            y_offset += 25

        card_idx = len(sprites) - 1
        clicked_idx = -1


        if left_clicked:
            for card in reversed(sprites):
                if card.faceup and card.rect.collidepoint(cursor):
                    print("card clicked")
                    clicked_idx = card_idx
                    break
                    
                card_idx -= 1

            if clicked_idx != -1:
                for i in range(clicked_idx, len(sprites)):
                    selected_cards.append(sprites[i])
                    sprites[i].selected = True

    def drop_stack(self, selected_cards):
        cursor = InputManager.cursor_pos
        bot_select = selected_cards[0]

        if bot_select.groups()[0] == self:
            return False

        if not self.sprites():
            collider: Rect = self.rect
            if collider.collidepoint(cursor):
                if bot_select.rank != Rank.KING:
                    return False
                else:
                    tab: Tableau = selected_cards[0].groups()[0]
                    tab.remove(selected_cards)

                    if tab.sprites():
                        tab.get_top_sprite().flip_up()

                    self.add(selected_cards)
                    return True

        else:
            top_sprite = self.get_top_sprite() 
            collider = top_sprite.rect
            if collider.collidepoint(cursor):
                if top_sprite.rank.value - 1 != bot_select.rank.value:
                    print("rank must decrease by one")
                    print("top: " + str(top_sprite.rank.value))
                    print("bot: " + str(bot_select.rank.value))
                    return False
                if top_sprite.color == bot_select.color:
                    print("colors must alternate")
                    return False
                else:
                    tab: Tableau = selected_cards[0].groups()[0]
                    # want to reset the selected_cards array but not re-add these

                    tab.remove(selected_cards)

                    if tab.sprites():
                        tab.get_top_sprite().flip_up()

                    self.add(selected_cards)
                    return True
    
