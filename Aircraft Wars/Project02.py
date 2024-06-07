import pygame
import random
from plane_sprites import *

class heroPlane(object):
      #创建英雄飞机
      def heroPlane(self):
          plane = pygame.image.load('img_3.png')
          #设置飞机的起始位置
          self.plane_site = pygame.Rect(100,700,102,126)
          while True:
              #1.设置刷新频率，一秒60次
              self.clock.tick(60)
              #2.在循环中不断改变飞机的位置
              self.plane_site.y -= 1
              if self.plane_site.y <= -126:
                  self.plane_site.y = 700
              #3.只要游戏窗口的资源有变化，需要重新传输，并且更新屏幕
              self.screen.blit(self.bg,(0,0))
              self.screen.blit(plane,self.plane_site)
              pygame.display.update()

class hero_Bg(object):
     # 创建背景面板
     def background(self):
         self.bg = pygame.image.load('img_1.png')

class Enemy(object):
     #创建敌机
     def bad_plane(self):
         self.enemies = pygame.image.load('img_4.png')
         #设置敌机的起始位置
         #需要使敌机随机出现
         self.enemy_site = pygame.Rect(random.randint(0,437),0,57,43)
         while True:
             #1.设置刷新频率，与英雄飞机相同，一秒60次
             self.clock.tick(60)
             #2.在循环中不断改变敌机的位置
             self.enemy_site += 1
             if self.enemy_site.y >= 700:
                 self.enemy_site = pygame.Rect(random.randint(0, 437), 0, 57, 43)
             #3.只要游戏窗口的资源有变化，需要重新传输，并且更新屏幕
             self.screen.blit(self.enemies,self.enemy_site)
             pygame.display.update()
