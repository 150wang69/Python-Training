import sys
import pandas as pd
import matplotlib.pyplot as plt
import requests
import json
import time
from datetime import datetime
import schedule
def send_get_request(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
        'Cookie':"CURRENT_FNVAL=4048; _uuid=A98EDDDE-97AD-9B1D-4A9E-D35794CAA3C195042infoc; buvid3=953F426F-EDBD-2CF4-2C03-0ACE2C1E019793357infoc; b_nut=1715172893; buvid4=A7824B70-B33F-6FD9-9C16-B780F2B088B294499-024050812-RUDu0o7X%2ByJJGXIbhNqw5g%3D%3D; buvid_fp=5d4be1b4d3dabe82569d550b2bc8548d; rpdid=|(JYlmJ)kYl|0J'u~ulu~k)ml; DedeUserID=3546390942714607; DedeUserID__ckMd5=524a7482d6b4d365; b_lsid=2610DF876_18FDB96143D; bsource=search_bing; enable_web_push=DISABLE; header_theme_version=CLOSE; home_feed_column=5; browser_resolution=1487-838; SESSDATA=399f8389%2C1732927999%2Cf3ddf%2A61CjDgOAY3VGmOJVKky3SjjB2dbHLB8BkCSVGFumN2QOIl5t4A-LuA0l_fHbSJ9KQDEXASVlc0aWNHS0lidDVvX1YwcnZZS0FIVGdvLWxnLUFtZ1Z3Vk1KMlBRZnNYY2l4WmVET1FKTkRMUFBYc0lEMU0za0FMWnl5QjhrWEVfd211dXJRNkxYM2hBIIEC; bili_jct=b03d0f285ac09f119b273d6d338cde3c; sid=g7tfgt8s; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTc2MzUyMDUsImlhdCI6MTcxNzM3NTk0NSwicGx0IjotMX0.8CXOns8QHJuM91oksd0frsL8CR4YLMNy2-IcJ1JRRyA; bili_ticket_expires=1717635145",
        'Referer':"https://www.bilibili.com/v/popular/rank/all/",
        'origin':"https://www.bilibili.com"
    }
    aidAndBvid = []
    try:
        # 发送GET请求
        response = requests.get(url,headers=headers)

        # 检查响应状态码
        if response.status_code == 200:
            print("请求成功！")
            print(response.text)
            s = json.loads(response.text)
            for key,value in s.items():
                if key == "data":
                    # print(value["list"][1])
                    for k in value["list"]:
                       if key == "data":
                           for k in value["list"]:
                               tmp = {
                                   "aid":k["aid"],
                                   "bvid": k["bvid"],
                                   "title": k["title"],
                                   "duration": k["duration"],
                                   "ctime": k["ctime"],
                                   "view": k["stat"]["view"],
                                   "coin":k["stat"]["coin"],
                                   "favorite":k["stat"]["favorite"],
                                   "like":k["stat"]["like"]
                               }
                               aidAndBvid.append(tmp)
                           return aidAndBvid
            print(aidAndBvid)


        else:
            print(f"请求失败，状态码：{response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"发生错误：{e}")


def bubble_sort_map(m):
    n = len(m)
    for i in range(n):
        for j in range(0, n - i - 1):
            if m[j]["view"] > m[j + 1]["view"]:
                m[j], m[j + 1] = m[j + 1], m[j]

    # 使用示例
def create_list(data):
    save_data = {
        "now":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "list":data
    }
    js = json.dumps(save_data)
    with open("1.json","a")as f:
        f.write(js+'\r\n')



def handle():
    now = datetime.now()
    formatTime = now.strftime("%Y-%m-%d %H:%M:%S")
    print(formatTime + "香香编程")
    url = 'https://api.bilibili.com/x/web-interface/popular/precious?page_size=100&page=1&web_location=333.934&w_rid=8f690ee1df1d07da33cb3aef419d6602&wts=1717489908'
    data = send_get_request(url)
    bubble_sort_map(data)
    data = data[:5]
    create_list(data)
def job():
    now = datetime.now()
    formatTime = now.strftime("%Y-%m-%d %H:%M:%S")
    print(formatTime + "香香编程")
# schedule.every(3).seconds.do(handle)
# handle()
# try:
#     while True:
#         schedule.run_pending()
#         time.sleep(1)
# except (KeyboardInterrupt, SystemExit):
#     print("收到退出信号")
#     sys.exit(0)
def show():
    data = {
        "cate":['ikun','mabaoguo','dasima','dingzhen','leibusi'],
        "value":[2.5,5,18,8,40]
    }
    df = pd.DataFrame(data)
    df.plot(kind='bar',x='cate',y='value')
    plt.title('xiangxiangcoding')
    plt.xlabel('king')
    plt.ylabel('value')
    plt.show()

show()