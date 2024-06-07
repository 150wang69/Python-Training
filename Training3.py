from bs4 import BeautifulSoup
import requests

content = requests.get("http://books.toscrape.com/").text
soup = BeautifulSoup(content, "html.parser")

# 我们想要查询页面中商品的价格，进入检查页面查看到商品价格是写在<p>标签里面的
# 并且所有关于商品价格的标签类“class”都是“price_color”
# 我们可以利用soup的findAll()方法对特定的元素进行查找，查找到所有<p>标签的class属性为price_color的值
all_pricese = soup.findAll("p", attrs={"class": "price_color"})
# findAll()方法会返回一个可迭代的对象，因此我们可以通过for循环一次操作返回的各个对象，得到我们想要的信息。
for price in all_pricese:
    print(price)  # 得到网页中所有出巡了价格信息的p标签

# 但是这样得到的是带有HTML标签的信息，会显得比较乱，所以我们可以使用string来提取实质性信息
# 更改后的代码如下：
for price in all_pricese:
    #print(price.string)  # string属性会把标签包围的文字返回给我们
    # 如果我们想要得到更加纯净的数字我们可以使用选择切片操作来完成。
    print(price.string[2:])

# 如果想要获得书名信息，会有些复杂，因为书名都是在a标签里面的，没有共性。
# 但是我们可以发现所有包含书名的a标签全都包含在h3标签里面，找到共性。
all_titles = soup.findAll("h3")
# 由于我们这次不用共同的属性标签来查找元素，所以不用添加attrs参数。
for title in all_titles:
    all_links = title.findAll("a")  # 如果在标签中只有唯一一个子标签，也可以直接使用find()查找。
    for link in all_links:
        print(link.string)