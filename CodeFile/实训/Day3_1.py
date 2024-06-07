import sys
from datetime import datetime
import time
import requests
import json

import schedule as schedule


def send_get_request(url):
    #User-Agent:User-Agent是一个特殊字符串头，它使得服务器能够识别客户端使用的操作系统及版本
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',

        'origin': 'https://www.bilibili.com',
        'referer': 'https://www.bilibili.com/v/popular/rank/all/',
        'cookie' : "buvid3=A916361A-CA79-99EF-C74D-10E06917AAF000023infoc; buvid4=95BC6031-BB88-B5FC-E807-2442AD61DF3501001-022110809-+VV2KmMJxFsEpRq9reSCqQ%3D%3D; rpdid=|(um~JJYRlYY0J'uYY))R~)lk; LIVE_BUVID=AUTO6616688479008925; buvid_fp=f4d1506fc4c0f8312eb8712bc9b44736; enable_web_push=DISABLE; header_theme_version=CLOSE; home_feed_column=4; DedeUserID=1690879677; DedeUserID__ckMd5=342dd30e111863be; b_nut=100; _uuid=6132E196-97A3-B18D-78D4-133F8114617B04938infoc; browser_resolution=1232-569; PVID=1; CURRENT_BLACKGAP=0; CURRENT_FNVAL=4048; bp_t_offset_1690879677=931964558426243127; SESSDATA=566f74e7%2C1732927370%2C7a51f%2A62CjDE8rAqZv8NlmTjp7_Zf-HQmLnK8EHx-AgmJ1cpSudOiCdO29dAxNaLM18hsN0Dz08SVmJCNEtlSFJuM3d2WkpDSmpRdGdNMzhrQWVhblI2emlCa2NwajFmMnNQaWZDUi01ajRnaUJwWlFTNDFCdHpYSGhRRkJUd2xEbGUyZkVrVkRkbEdVeThRIIEC; bili_jct=96d33ab1d50f68a9181a85b866184ed9; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTc2MzQ1OTQsImlhdCI6MTcxNzM3NTMzNCwicGx0IjotMX0.kiqBFR2dPmy7oKhLo-wQcW45KDo9vuWnFM-In-xLrSI; bili_ticket_expires=1717634534; b_lsid=5B13ECA9_18FDD01CD8A; bsource=search_baidu; sid=8ay7sbd3"}
    try:
        # 发送GET请求
        response = requests.get(url,headers=headers)
        aidAndBvid =[]
        # 检查响应状态码
        if response.status_code == 200:
            print("请求成功！")
            data = json.loads(response.text)
            # print(data)
            for key, value in data.items():
                if key == 'data':
                    for k in value['list']:
                       tmp ={
                           "aid": k["aid"],
                           "bvid": k["bvid"],  # B站视频自动形成的算法,也叫bv号
                           "title": k["title"],
                           "duration": k["duration"],  # 时长
                           "ctime": k["ctime"],  # 视频创建的时间戳
                           "view": k["stat"]["view"],  # 播放量
                           "coin": k["stat"]["coin"],  # 投币
                           "favorite": k["stat"]["favorite"],  # 收藏
                           "like": k["stat"]["like"]  # 点赞
                       }
                       aidAndBvid.append(tmp)
                    # print(aidAndBvid)
                    # print(type(aidAndBvid))
                    # json_aidAndBvid = json.dumps(aidAndBvid,ensure_ascii=False)  #ensure_ascii=False 显示正常的中文
                    # print(json_aidAndBvid)
                    # print(type(json_aidAndBvid))
                    return aidAndBvid

        else:
            print(f"请求失败，状态码：{response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"发生错误：{e}")


def bubble_sort_map(data):
    m=data
    n = len(m)
    for i in range(n):
        for j in range(0,n-i-1):
            if m[j]["view"] > m[j+1]["view"]:
                m[j],m[j+1] = m[j+1],m[j]
    print(m)
def create_file_list(data):
    save_data={
        "now":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "list":data
    }
    js = json.dumps(save_data)
    with open('bilibili.json','a')as file:
        file.write(js+'\r\n')

def handle():
    now=datetime.now()
    formatTime=now.strftime("%Y-%m-%d %H:%M:%S")
    print(formatTime+".....")
    data=send_get_request('https://api.bilibili.com/x/web-interface/popular/precious?page_size=100&page=1&web_location=333.934&w_rid=3958c471841e5a04c2f49cbf70fc9b3f&wts=1717379441')
    bubble_sort_map(data)
    print(data[:10])
    for detail in data[:5]:
      print(detail["view"])

def job():
    now = datetime.now()
    formatTime = now.strftime("%Y-%m-%d %H:%M:%S")
    print(formatTime+"。。。。。")

# schedule.every(3).seconds.do(handle)
# handle()

schedule.every(3).seconds.do(job)
job()

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except (KeyboardInterrupt,SystemExit):
    print("收到退出信号")
    sys.exit(0)
# create_file_list(data)