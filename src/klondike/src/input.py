from typing import Tuple
import pygame
from pygame import mouse
from pygame.event import Event


class InputManager:
    """
    class for managing the pygame event queue, 
    provides class method interface for determing clicks, etc
    """

    @classmethod
    def init(cls):
        cls.cursor_pos: Tuple[int, int] = (0, 0)      # 鼠标当前位置 (x, y)
        cls.cursor_rel_pos: Tuple[int, int] = (0, 0)  # 鼠标相对移动 (dx, dy)

        cls.mouse = [False, False, False]             # [左键, 中键, 右键] 是否按下
        # per frame
        cls.mouse_down = [False, False, False]        # 每帧是否按下（瞬时状态）
        cls.mouse_up = [False, False, False]          # 每帧是否松开（瞬时状态）


    @classmethod
    def frame_start(cls):
        cls.mouse_down = [False, False, False]  # 每帧重置按下状态
        cls.mouse_up = [False, False, False]    # 每帧重置松开状态

            
    @classmethod
    def process_input(cls, event: Event):

        if event.type == pygame.MOUSEBUTTONDOWN:
            idx = event.button - 1            # 1=左键, 2=中键, 3=右键
            cls.mouse_down[idx] = not cls.mouse[idx]  # 瞬时按下
            cls.mouse[idx] = True             # 设置持续按下状态

        elif event.type == pygame.MOUSEBUTTONUP:
            idx = event.button - 1
            cls.mouse_up[idx] = cls.mouse[idx]  # 瞬时松开
            cls.mouse[idx] = False              # 取消持续按下状态


    @classmethod
    def MOUSE_LEFT(cls) -> bool:        # 左键是否持续按下
        return cls.mouse[0]

    @classmethod
    def MOUSE_LEFT_DOWN(cls) -> bool:   # 左键是否刚按下（瞬时）
        return cls.mouse_down[0]

    @classmethod
    def MOUSE_LEFT_UP(cls) -> bool:     # 左键是否刚松开（瞬时）
        return cls.mouse_up[0]


    @classmethod
    def MOUSE_RIGHT(cls) -> bool:
        return cls.mouse[2]

    @classmethod
    def MOUSE_RIGHT_DOWN(cls) -> bool:
        return cls.mouse_down[2]

    @classmethod
    def MOUSE_RIGHT_UP(cls) -> bool:
        return cls.mouse_up[2]


