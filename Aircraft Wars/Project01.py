import pygame
#1.导入pygame
import random
from plane_sprites import *
#初始化pygame
pygame.init() #导入并初始化所有pygame模块，使用其他模块前，必须先嗲用init()
#这步是所有的开始，必须先进行初始化。
screen = pygame.display.set_mode((480, 700))  #初始化游戏显示窗口,参数为一个元组。
# pygame.display.update()  刷新屏幕内容显示，稍后使用。
# while True:   #临时的死循环
#     pass
#可以暂时让游戏窗口不消失。
#理解游戏中的坐标： 原点为左上角！！！！
#在游戏中，所有可见的元素都是以矩形区域来描述位置的。
#需要描述的位置有两个，(x,y),(width,height)
#x,y是指左上角的坐标。
#pygame.Rect()是一个比较特殊的类，内部只是封装了一些数字计算，不执行初始化init()也能运行。
#Rect内部可以通过x,y获取当前矩形区域的坐标。
#Rect内部可以通过wigth和height，获取矩形区域的大小
#也可以通过size获取当前矩形区域的大小。
# hero_rect = pygame.Rect(150,300,102,126)
# print('当前矩形区域的原点为',(hero_rect.x,hero_rect.y))
# print('当前矩形区域的宽高为',(hero_rect.width,hero_rect.height))
# print("当前矩形区域的大小为",hero_rect.size)
#加载图像的数据
background = pygame.image.load('img_1.png')
plane = pygame.image.load("img_3.png")
enemy = pygame.image.load('img_4.png')
bullet = pygame.image.load('bullet1.png')
#使用游戏屏幕对象
# screen.blit(background,(0,0))
# screen.blit(plane,(100,500))
# screen.blit(enemy,(0,0))
# screen.blit(bullet,(251,563))
#更新屏幕显示
# pygame.display.update()
#不使用pygame的clock时钟时
# i= 0
# while True:
#     print(i)
#     i += 1
#     pass
#先初始化一个时钟对象：创建一个时钟对象 我们需要一秒钟执行60次。
#利用Clock时钟：
clock = pygame.time.Clock()
#让英雄动起来，在垂直方向移动
#Rect矩形区域，定义飞机位置和大小
enemySite = random.randint(0, 437)
hero_rect = pygame.Rect(200,500,102,126)
hero_rect02 = pygame.Rect(enemySite, 0, 57, 43)
bulletSite = pygame.Rect(150,690,5,11)

#需求：通过GameSprites创建敌机
enemy1 = GameSprites('img_4.png',1)
enemy2 = GameSprites('img_4.png',2)
enemy3 = GameSprites('img_4.png',3)
enemy4 = GameSprites('img_4.png',4)
enemy5 = GameSprites('img_4.png',5)
enemy1.rect.x = random.randint(0,437)
enemy2.rect.x = random.randint(0,437)
enemy3.rect.x = random.randint(0,437)
enemy4.rect.x = random.randint(0,437)
enemy5.rect.x = random.randint(0,437)
#创建出来的精灵需要添加到精灵组
enemy_group = pygame.sprite.Group(enemy1,enemy2,enemy3,enemy4,enemy5)
while True:
    # 1.参数为一秒钟刷新次数 一秒钟刷新60次
    # 每秒刷新60帧，fps frames per second 是高清画质 流畅
    # 让敌机做动画 ----> 设置游戏时钟。
    clock.tick(60)
    # 2.在循环体中，不断改变英雄y轴的位置
    hero_rect.y -= 1
    # bulletSite.y -= 1
    # 但是还需要让飞机循环，运动到顶部回到底部
    if hero_rect.y <= -126:
        hero_rect.y = 700
    # 飞机需要遵循用户的指令来移动，需要监听用户的动作（事件）
    # event_list = pygame.event.get() #可以获取当前用户操作的所有指令。
    # if bulletSite.y <= -126:
    #     bulletSite.y = 700
    event_list = pygame.event.get()
    # if len(event_list) > 0:
    #     print(event_list)
    for event in event_list:
        #如果点击了退出：
        if event.type == pygame.QUIT :
          print("退出游戏")
          pygame.quit()
          exit()
    # 3.只要游戏窗口的资源有变化，重新传输，并且更新屏幕
    # 4.注意：经常出现问题的位置，每一次都需要重新将背景图片添加到游戏窗口中
    screen.blit(background,(0,0))
    screen.blit(plane,hero_rect)
    # screen.blit(bullet, bulletSite)
    # 循环过程中，不断更改敌机位置，显示敌机
    enemy_group.update()
    #将敌机更新后的位置，传到屏幕上
    enemy_group.draw(screen)
    pygame.display.update()
#如果想要超出窗口，需要入场动画和出场动画。



#设置填充颜色：RGB
#(red,green,blue):0-255(255,0,0)-->red(25,255,255)-->white
#十六进制的RGB值：#ff0000----->红色#000000----->黑色#00ff00----->绿色
#screen.fill(225,225,225) #设置颜色
#image = pygame.image.load("C:\Users\ASUS\Desktop\背景图.png")
#screen.fill = (14,56,20)
# class PlaneGame(object):
#     '''飞机大战主程序'''
#         #1.创建游戏窗口
#         # set_mode((width,height))--->单位是像素
#         screen = pygame.display.set_mode((600, 400))
#         screen.fill(14,56,20) #设置颜色

#退出pygame
pygame.quit() #卸载所有的pygame模块，在游戏结束前调用。
#pygame.display.flip() #将前面的内容渲染到屏幕上，一般都会放在最后以节约cpu内存
