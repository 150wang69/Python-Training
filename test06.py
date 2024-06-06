# 导入requests库，用于发送网络请求
import requests
# 导入BeautifulSoup库，用于解析HTML内容
from bs4 import BeautifulSoup
# 导入time库，虽然在这段代码中并没有使用到
import time

# 定义函数：请求网页
def page_request(url, ua):
    # 发送GET请求，获取网页内容，headers参数用于设置请求头信息
    response = requests.get(url, headers=ua)
    # 将获取到的网页内容解码为utf-8格式的字符串
    html = response.content.decode('utf-8')
    # 返回解码后的HTML内容
    return html


# 定义函数：解析网页
def page_parse(html):
    # 使用BeautifulSoup解析HTML内容，指定解析器为'lxml'
    soup = BeautifulSoup(html, 'lxml')
    # 获取网页的标题信息
    title = soup('title')
    # 查找包含诗句、出处和链接的HTML元素
    info = soup.select('body > div.main3 > div.left > div.sons > div.cont')
    # 查找诗句链接的HTML元素
    sentence = soup.select('div.left > div.sons > div.cont > a:nth-of-type(1)')
    # 初始化诗句列表和链接列表
    sentence_list = []
    href_list = []

    # 遍历所有包含诗句信息的HTML元素
    for i in range(len(info)):
        curInfo = info[i]
        poemInfo = ''
        # 将当前元素的文本内容（去除换行符）拼接并赋值给poemInfo
        poemInfo = poemInfo.join(curInfo.get_text().split('\n'))
        # 将诗句信息添加到诗句列表中
        sentence_list.append(poemInfo)

        # 获取当前诗句的链接，并拼接成完整的URL
        href = sentence[i].get('href')
        href_list.append("https://so.gushiwen.org" + href)

        # 注释说明：sentence和poet数量可能不符，这部分代码被注释掉了
    # sentence = soup.select('div.left > div.sons > div.cont > a:nth-of-type(1)')
    # poet = soup.select('div.left > div.sons > div.cont > a:nth-of-type(2)')
    # for i in range(len(sentence)):
    #     temp = sentence[i].get_text() + "---" + poet[i].get_text()
    #     sentence_list.append(temp)
    #     href = sentence[i].get('href')
    #     href_list.append("https://so.gushiwen.org" + href)

    # 返回一个包含链接列表和诗句列表的列表
    return [href_list, sentence_list]


# 定义函数：将信息保存到txt文件
def save_txt(info_list):
    # 导入json库，用于将信息转换为json格式
    import json
    # 以追加模式打开文件，并设置编码为utf-8
    with open(r'sentence.txt', 'a', encoding='utf-8') as txt_file:
        # 遍历诗句列表
        for element in info_list[1]:
            # 将诗句信息转换为json格式，并写入文件，每行之间添加换行符
            txt_file.write(json.dumps(element, ensure_ascii=False) + '\n\n')

        # 定义子网页处理函数：请求子网页并返回HTML内容


def sub_page_request(info_list):
    # 获取链接列表
    subpage_urls = info_list[0]
    # 设置请求头信息
    ua = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36'}
    # 初始化一个空列表，用于存储子网页的HTML内容
    sub_html = []
    # 遍历链接列表，请求每个子网页的内容，并添加到sub_html列表中
    for url in subpage_urls:
        html = page_request(url, ua)
        sub_html.append(html)
        # 返回子网页的HTML内容列表
    return sub_html
# 子网页处理函数：解析子网页，爬取诗句内容
# 定义函数：解析子网页并返回诗句列表
def sub_page_parse(sub_html):
    poem_list = []  # 初始化一个空列表，用于存储解析出的诗句
    for html in sub_html:  # 遍历所有子网页的HTML内容
        soup = BeautifulSoup(html, 'lxml')  # 使用BeautifulSoup解析当前子网页的HTML
        # 查找包含诗句的HTML元素
        poem = soup.select('div.left > div.sons > div.cont > div.contson')
        if len(poem) == 0:  # 如果找不到包含诗句的元素，则跳过当前子网页
            continue
        poem = poem[0].get_text()  # 获取第一个包含诗句的元素的文本内容
        poem_list.append(poem.strip())  # 去除诗句文本两端的空白字符，并添加到诗句列表中
    return poem_list  # 返回解析出的诗句列表


# 定义函数：将诗句列表保存到txt文件
def sub_page_save(poem_list):
    import json  # 导入json库
    with open(r'poems.txt', 'a', encoding='utf-8') as txt_file:  # 以追加模式打开文件
        for element in poem_list:  # 遍历诗句列表
            txt_file.write(json.dumps(element, ensure_ascii=False) + '\n\n')  # 将诗句转换为json格式并写入文件


# 当这个脚本被当作主程序运行时，以下代码将被执行
if __name__ == '__main__':
    print("**************开始爬取古诗文网站********************")  # 输出开始爬取的提示信息
    ua = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36'}  # 设置请求头信息
    poemCount = 0  # 初始化一个计数器，用于记录爬取到的古诗词名句数量
    # 循环请求4个页面
    for i in range(1, 5):
        # 设置请求的URL，注意这里的URL与原始代码中的不同，已经更正为正确的URL
        url = 'https://so.gushiwen.cn/mingjus/default.aspx?page=%d' % i
        print(url)  # 输出当前请求的URL
        # 发送请求并获取HTML内容
        html = page_request(url, ua)
        # 解析HTML内容，获取链接和诗句列表
        info_list = page_parse(html)
        # 保存链接和诗句列表到txt文件
        save_txt(info_list)
        # 开始处理子网页
        print("开始解析第%d" % i + "页")  # 输出开始解析当前页面的提示信息
        # 请求子网页并获取HTML内容列表
        sub_html = sub_page_request(info_list)
        # 解析子网页的HTML内容，获取诗句列表
        poem_list = sub_page_parse(sub_html)
        # 将诗句列表保存到txt文件
        sub_page_save(poem_list)

        # 更新古诗词名句的数量
        poemCount += len(info_list[0])

    print("****************爬取完成***********************")  # 输出爬取完成的提示信息
    print("共爬取%d" % poemCount + "个古诗词名句")  # 输出爬取到的古诗词名句的总数
    print("共爬取%d" % poemCount + "个古诗词")  # 这里应该是一个重复的信息，因为前面已经输出了古诗词名句的总数
