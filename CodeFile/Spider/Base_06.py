import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# print(ssl.get_default_verify_paths())
#通过urllib.request模块事先发送GET请求获取网页内容
response = urllib.request.urlopen("https://www.hist.edu.cn/index/sy/kyyw.htm")
content = response.read().decode('utf-8')
soup = BeautifulSoup(content,'html.parser')
#这里需要查看页面的源代码确定class的名字。
divs = soup.find_all('div',{'class':"list-main-warp"})
lists = divs[0].find_all('li')
#写操作
with open("news.txt",'w',encoding='utf8') as fp:
    for new_li in lists:
        url1 = "https://www.hist.edu.cn/"
        url2 = new_li.find_all('a')[0].get('href')
        new_url = urljoin(url1,url2)
        title = new_li.find_all('a')[0].get('title')
        fp.write(new_url + "," + title + '\n')
print("爬取成功！")
# html = response.read()
# print(html)

