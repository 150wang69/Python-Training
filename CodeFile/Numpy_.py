import numpy as np

#由list创建array
a=[1,2,3,4,5] #创建简单的列表
b=np.array(a) #将列表转换为数组
print("b:",b) #输出数组
print("b的长度",b.size) #输出数组长度
print("b的形状",b.shape) #输出数组的形状
print("b的维度",b.ndim) #输出数组的维度

#numpy自身函数创建
c=np.array([1,2,3,4,5])
d=np.array(range(1,6))
e=np.arange(1,6)
print("c:",c," d:",d,"e:",e)
"""
1.列表中的元素的数据类型可以不同，但是数组中的元素的数据类型必须相同。
2.列表不可以进行数学四则运算，但是数组可以。
3.相对于数组，列表会占用更多的存储空间。
"""

#列表和数组的区别
print("a的类型:",type(a))
print("b的类型:",type(b))
print(a+a) #列表相加直接向后加入元素，长度改变
print(b+b) #数组相加直接进行四则运算

#numpy特殊数组
"""
1.ones()创建一个矩阵，内部元素均为1.第一个参数提供维度，第二个参数提供类型
"""
f=np.ones([2,3],int)
print("f:\n",f)
"""
2.empty()创建一个矩阵，内部元素是无意义的0数值，第一参数提供维度，第二个参数提供类型
"""
g=np.empty([2,3],int)
print("g:\n",g)
