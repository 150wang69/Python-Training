import pygame
import random

#敌机的定时器常量
#需求：通过定时器，每隔1秒添加一架飞机
#pygame.time.set.timer(事件id,间隔时间单位ms)
#首先需要创建 敌机的事件id，用户的事件id
#添加敌机事件id
enemy_event =pygame.USEREVENT
#添加英雄发射子弹事件（用户事件）
fire_event = pygame.USEREVENT + 1

class GameSprites(pygame.sprite.Sprite):
    #初始化方法
    def __init__(self,image_name,speed=1):
        #必须要调用父类的init方法
        super().__init__()
        #1.记录精灵的图片
        self.image = pygame.image.load(image_name)
        #2.记录精灵尺寸
        self.rect = self.image.get_rect()
        #3.记录速度
        self.speed = speed

    def update(self):
        #默认在垂直方向上移动
        self.rect.y += self.speed

#背景精灵，继承GameSprites
#图片有两张，第一张图片（0，0），第二张图片 （0，自身高度）
#背景图片的尺寸
screen = pygame.Rect(0,0,480,700)
class BackGround(GameSprites):

    def __init__(self):
        #调用父类方法实现精灵的创建
        image_name = "img_1.png"
        super().__init__(image_name)
    def update(self):
        #调用父类方法实现
        super().update()
        #循环动画，判断图片的位置，如果>=700,则重新开始
        if self.rect.y >= self.rect.height:
            self.rect.y = -700

class Enemy(GameSprites):

    def __init__(self):
        #1.调用父类方法创建敌机精灵，并指定敌机图像
        image_name = 'img_4.png'
        super().__init__(image_name)
        #2.设置敌机的随机速度 1-3
        self.speed = random.randint(1,3)  #randint()左右极限都能取到
        #3.设置敌机的随机位置 水平方向
        self.rect.x = random.randint(0,437)

    def update(self):
        #1.调用父类，让敌机在垂直方向移动
        super().update()
        #2.如果敌机飞出屏幕，从精灵组删除
        if self.rect.y >= screen.height:
            print('敌机飞出屏幕')
            self.kill()

    #重写__del__方法，打印敌机被销毁
    def __del__(self):
        print('飞机被kill...%s'%self.rect)

class Hero_Plane(GameSprites):

    def __init__(self):
        #战机的图片，垂直方向不移动，速度为0
        super().__init__('img_3.png',0)
        #1.设置初始位置，水平居中，垂直方向距离底部120
        self.rect.centerx = screen.centerx
        self.rect.bottom = screen.bottom - 120
        #方向：默认为1（水平），2（垂直）
        self.direction = 1
        #2..创建子弹的精灵组
        self.bullets = pygame.sprite.Group()

    def update(self):

        if self.direction == 1:
            # 1.英雄飞机在水平方向上移动
            self.rect.x += self.speed
            # 2.判断屏幕边界
            if self.rect.left < 0:
                self.rect.left = 0
            elif self.rect.right > screen.right:
                self.rect.right = screen.right
        else :
            #1.飞机在垂直方向上移动
            super(Hero_Plane, self).update()
            #2.判断屏幕边界
            if self.rect.top < 0:
                self.rect.top = 0
            if self.rect.bottom > 700:
                self.rect.bottom = 700

    def fire(self):
        print('发射子弹')
        #发射子弹需要开启定时器
        #实现一次发射三枚子弹
        for i in range(1,4):
            #创建子弹精灵
            bullets = Bullets()
            #设置位置
            #子弹的位置：水平在飞机中间，垂直在飞机头的 +20 处
            bullets.rect.bottom = self.rect.y - i * 20
            bullets.rect.centerx = self.rect.centerx
            #将子弹精灵添加到精灵组
            self.bullets.add(bullets)

class Bullets(GameSprites):
    
    def __init__(self):
        super().__init__('bullet1.png',-2)

    def update(self):
        super(Bullets, self).update()
        #判断是否飞出屏幕
        if self.rect.bottom <= 0:
            self.kill()


