from bs4 import BeautifulSoup
import requests

headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}
for start_num in range(0,250,25):
    response = requests.get(f"http://movie.douban.com/top250?start={start_num}",headers=headers)
    html = response.text
    soup = BeautifulSoup(html,"html.parser")
    # all_divs = soup.findAll("div",attrs={"class":"hd"})
    # for div in all_divs:
    #     all_links = div.findAll("a")
    #     for link in all_links:
    #         # all_titles = link.findAll("span",attrs={"class":"title"})
    #         # for title in all_titles:
    #         #     print(title.string)


    all_titles = soup.findAll("span",attrs={"class":"title"})
    for title in all_titles:
        # print(title.string)
        title_string = title.string
        if "/" not in title_string:
            print(title_string)
    #或者直接使用find()