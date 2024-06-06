# 要求：使用openpyxl包操作打开此文件，编写程序统计在此表中合作电影数目最多的两个演员。

from openpyxl import load_workbook

#首先打开所需文件
wb = load_workbook("电影导演演员信息表.xlsx")
#再打开需要的工作表
ws = wb.worksheets[0]
#1.首先要获取每个演员对应的电影，使用字典来表示，关键字是演员，值是出演的电影，用集合表示
actors_films = dict()#初始化一个字典
# 使用for循环遍历工作表的每一行，获取演员和出演电影
for index,row in enumerate(ws.rows):
    if index == 0:
        continue #如果索引等于0则跳出本次循环，即跳过表头
    film,actors = row[0].value,row[2].value.split('，') #使用逗号将值分隔开
    for actor in actors: #分开后遍历演员列表
        actors_films[actor] = actors_films.get(actor,set()) | {film}
        #将演员及其出演的电影添加到actors_films字典中。如果演员已经在字典中，则获取该演员已出演的电影集合，否则创建一个空集合。然后，通过|操作符（集合的并集操作），
        # 将新的电影名称添加到演员已出演的电影集合中，最后将更新后的集合赋值给该演员键。这样就实现了将演员和出演的电影信息存储到字典中的操作。
        #这里使用了字典的 get() 方法。get() 方法用于获取字典中指定键的值。如果键存在于字典中，则返回对应的值；如果键不存在，则返回指定的默认值。
        # 在这里，如果 actor 这个键不存在于 actors_films 字典中，那么 get() 方法将返回一个空集合 set()，作为默认值。
        #这样做的目的是确保即使演员尚未出现过，也能为其创建一个空的电影集合。
        #|: 这是集合的并集操作符。它用于将两个集合的元素合并成一个新的集合，保留两个集合中的所有唯一元素。在这里，它用于将原来的演员已出演的电影集合与新的电影名称合并。
        #这样做的目的是将新电影名称添加到该演员已出演的电影集合中。


#打印出来对应的数据
print(actors_films)
actors = actors_films.keys() #使用.keys()获取字典的关键字，即所有演员
actors = tuple(actors) #将获取的关键字放入元组中
print(actors)
max = 0 #设置max变量进行统计比较
co_actors = () #用来存放比较得到的出演电影最多的演员
for index,actor1 in enumerate(actors):
    for actor2 in actors[index+1:]:
        common = len(actors_films[actor1] & actors_films[actor2]) #即合作的电影数
        # print(actors_films[actor1] & actors_films[actor2]) #输出合作的相同的电影
        if common > max: #判断并给max赋值
            max = common
            co_actors = (actor1,actor2) #得到两个合作电影最多的演员

print(max,co_actors)

