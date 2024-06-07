#游戏主程序
#1.封装 主游戏类
#2.创建 游戏对象
#3.启动游戏
import pygame
from plane_sprites import *
#导入并初始化所有pygame模块，使用其他模块前，必须先使用init()
#这步是所有的开始，必须先进行初始化。
pygame.init()

class PlaneGame(object):
    #1.初始化方法
    def __init__(self):

        print('游戏初始化')

        #1.创建初始窗口
        self.screen = pygame.display.set_mode((480,700))
        #2.创建时钟
        self.clock = pygame.time.Clock()
        #3.创建精灵
        self.__create_sprites()
        #4.需求：通过定时器每隔1s添加一架飞机
        # pygame.time.set_timer(事件id,间隔时间单位ms)
        pygame.time.set_timer(enemy_event, 500)
        pygame.time.set_timer(fire_event, 500)

    #(1.1)私有方法：创建精灵
    def __create_sprites(self):
        #1.创建背景精灵和精灵组
        bg1 = BackGround()
        bg2 = BackGround()
        #第二张图片的位置是，负的自身高度
        bg2.rect.y = -bg2.rect.height
        self.back_group = pygame.sprite.Group(bg1,bg2)
        #2.创建敌机精灵组
        self.enemy_group = pygame.sprite.Group()
        #3.创建英雄飞机精灵组
        self.hero = Hero_Plane()
        self.hero_group = pygame.sprite.Group(self.hero)

    #2.开始游戏
    def start_game(self):

        print('开始游戏')

        while True:
            #1.设置刷新频率
            self.clock.tick(60)
            #2.事件监听
            self.__event_handle()
            #3.碰撞检测
            self.__check_collide()
            #4.更新精灵组
            self.__update_sprites()
            #5.更新屏幕显示
            pygame.display.update()

    #(2.1)事件监听
    def __event_handle(self):
        event_list = pygame.event.get()
        # if len(event_list) > 0:
        #    print(event_list)

        #监听游戏是否退出
        for event in event_list:
            if event.type == pygame.QUIT:
                self.__game_over()

            #如果是定时器们就可以添加敌机，监听敌机出现
            elif event.type == enemy_event:
                print('出击')
                #创建敌机精灵
                enemy = Enemy()
                self.enemy_group.add(Enemy())

            # 战机移动，检测用户的键盘事件
            #如果按下右键向右移动，速度为2
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                print("按下右键")
                self.hero.speed = 3
                self.hero.direction = 1
            # 如果按下右键向左移动，速度为-2
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                print("按下左键")
                self.hero.speed = -3
                self.hero.direction = 1
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                print('按下上键')
                self.hero.speed = -3
                self.hero.direction = 2
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                print('按下下键')
                self.hero.speed = 3
                self.hero.direction = 2
            # 让英雄发射子弹
            elif event.type == fire_event:
                self.hero.fire()
            else :
                #如果不是左键或右键，应该让速度归为零，这样就不会出现按下左键就一直往左走
                self.hero.speed = 0

    #(2.2)碰撞检测（子弹销毁敌机）
    def __check_collide(self):
        #1.敌机精灵组与子弹精灵组检测碰撞
        pygame.sprite.groupcollide(self.hero.bullets,self.enemy_group,True,True)
        #2.英雄精灵与敌机组检查碰撞
        results = pygame.sprite.spritecollide(self.hero,self.enemy_group,True)
        #发生碰撞
        if len(results) > 0:
            self.hero.kill()
            self.__game_over()

    #(2.3)精灵族更新和绘制
    def __update_sprites(self):
        # #更新精灵组的位置
        # self.back_group.update()
        # #将更新后的位置传送到屏幕上
        # self.back_group.draw()

        # 也可以使用循环进行优化
        for group in [self.back_group,self.enemy_group,self.hero_group,self.hero.bullets]:
            group.update()
            group.draw(self.screen)

    #(2.4)游戏结束
    def __game_over(self):
        print('退出游戏')
        #退出游戏
        pygame.quit()
        #程序停止运行
        exit()

#注意这个代码没有缩进，不是PlaneGame类的代码
if __name__ == '__main__':
        game = PlaneGame()
        game.start_game()
