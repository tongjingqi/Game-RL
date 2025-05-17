import sys
import pygame
from pygame.locals import *
import random

class Block:
    blk_color = [(255, 255, 255),(255, 255, 0),(255, 0, 255),(0, 255, 255),(255, 0, 0),(0, 255, 0),(0, 0, 255),(32,32,32)]
    BLANK = 7
    type_coord=[[[-1,0],[0,0],[1,0],[2,0]]\
        ,[[-1,0],[0,0],[1,0],[0,1]]\
        ,[[-1,0],[0,0],[-1,1],[0,1]]\
        ,[[-1,0],[0,0],[0,1],[1,1]]\
        ,[[0,0],[1,0],[-1,1],[0,1]]\
        ,[[-1,0],[0,0],[1,0],[1,1]]\
        ,[[-1,0],[0,0],[1,0],[-1,1]]]
    type_rotate = []
    
    def __init__(self,x,y,blk,angle):
        self.x = x
        self.y = y
        self.blk = blk
        self.angle = angle
        
    @staticmethod
    def rotate(no):
        rt_all = []
        rt = Block.type_coord[no][:]
        cx,cy=0,0
        for b in range(4):
            rt[b][0],rt[b][1] = rt[b][0]*4,rt[b][1]*4
            cx += rt[b][0]
            cy += rt[b][1]
        cx = (cx)//8*2 if no !=6 else (cx+4)//8*2
        cy = (cy)//8*2 if no !=6 else (cy-4)//8*2
        rt_all.append(rt)
        for r in range(3):
            rt_new = []
            for b in range(4):
                rt_new.append([cx + (cy-rt[b][1]),cy-(cx-rt[b][0])])
            rt_all.append(rt_new)
            rt = rt_new
        for r in range(4):
            for b in range(4):
                rt_all[r][b][0] //= 4
                rt_all[r][b][1] //= 4
        return rt_all
    @staticmethod
    def init_rotate():
        for r in range(7):
            Block.type_rotate.append(Block.rotate(r))

class TRS:
    screen = None
    map = [[Block.BLANK]*10 for i in range(20)]
    STATUS = 0
    cbk = None

    def __init__(self,screen):
        TRS.screen = screen

    @staticmethod
    def action(key_pressed):
        if(key_pressed[K_LEFT] and TRS.check_action(TRS.cbk.x-1,TRS.cbk.y,TRS.cbk.blk,TRS.cbk.angle)):
            TRS.cbk.x -= 1
        elif (key_pressed[K_RIGHT] and TRS.check_action(TRS.cbk.x+1,TRS.cbk.y,TRS.cbk.blk,TRS.cbk.angle)):
            TRS.cbk.x += 1
        elif (key_pressed[K_UP] and TRS.check_action(TRS.cbk.x,TRS.cbk.y,TRS.cbk.blk,TRS.cbk.angle+1)):
            TRS.cbk.angle += 1
        elif (key_pressed[K_DOWN] and TRS.check_action(TRS.cbk.x,TRS.cbk.y+1,TRS.cbk.blk,TRS.cbk.angle)):
            TRS.cbk.y += 1
            
    @staticmethod
    def new_blk():
        TRS.cbk = Block(5,0,random.randint(0,6),0)
    @staticmethod
    def check_action(x,y,blk,angle):
        tr = Block.type_rotate[blk][angle%4]
        for b in range(4):
            bx,by = x + tr[b][0],y + tr[b][1]
            if(bx<0 or bx>9 or by <0 or by>19 or TRS.map[by][bx]!=Block.BLANK):
                return False
        return True
    @staticmethod
    def check_drop():
        if TRS.check_action(TRS.cbk.x,TRS.cbk.y+1,TRS.cbk.blk,TRS.cbk.angle):
            TRS.cbk.y += 1
        else:
            TRS.STATUS = 2
            
    @staticmethod
    def check_clear():
        blk = Block.type_rotate[TRS.cbk.blk][TRS.cbk.angle%4]
        row = list({TRS.cbk.y + blk[i][1] for i in range(4)})
        row.sort()
        row.reverse()
        for b in range(4):
            TRS.map[TRS.cbk.y + blk[b][1]][TRS.cbk.x + blk[b][0]] = TRS.cbk.blk
        del_rows = 0
        for r in row:
            if not (Block.BLANK in TRS.map[r]):
                TRS.map.pop(r)
                del_rows += 1
        for d in range(del_rows):
            TRS.map.insert(0,[Block.BLANK for i in range(10)])
            
    @staticmethod
    def print_game():
        TRS.screen.fill((0, 0, 0))
        for row in range(20):
            for col in range(10):
                pygame.draw.rect(TRS.screen, Block.blk_color[TRS.map[row][col]], ((col*21,row*21), (20, 20)), 0)
        blk = Block.type_rotate[TRS.cbk.blk][TRS.cbk.angle%4]
        for b in range(4):
            pygame.draw.rect(TRS.screen, Block.blk_color[TRS.cbk.blk], (((TRS.cbk.x+blk[b][0])*21,(TRS.cbk.y+blk[b][1])*21), (20, 20)), 0)
class App:
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode((300,430))
        Block.init_rotate()
        TRS(screen)
        
    def main(self):
        clock = pygame.time.Clock()   # 创建游戏时钟
        count = 1
        # 进入游戏循环
        while True:
            # 设置刷新帧率
            clock.tick(15)
         
            # 事件检测
            for event in pygame.event.get():
                if event.type == pygame.QUIT:   # 退出事件
                    sys.exit()
                    
            if TRS.STATUS == 0:
                TRS.new_blk()
                if TRS.check_action(TRS.cbk.x,TRS.cbk.y,TRS.cbk.blk,TRS.cbk.angle):
                    TRS.STATUS = 1
                else:
                    TRS.STATUS = 3
                    font = pygame.font.Font(None, 50)  # 创建字体对象
                    text_surface = font.render("GAME OVER", True, (255, 0, 0))  # 渲染文字
                    text_rect = text_surface.get_rect(center=(150, 215))  # 定位到屏幕中心
                    TRS.screen.blit(text_surface, text_rect)  # 绘制文字
                    print("GAME OVER")
            elif TRS.STATUS == 1:
                TRS.action(pygame.key.get_pressed())
                if count % 10 == 0:
                    TRS.check_drop()
            elif TRS.STATUS == 2:
                TRS.check_clear()
                TRS.STATUS = 0

            TRS.print_game()
            pygame.display.update()   #刷新屏幕
            count += 1
 
App().main()
