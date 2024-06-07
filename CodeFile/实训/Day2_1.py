import requests
import json

#这个代码请求成功
def send_get_request(url):
    headers = {
        'User-Agent':
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        'Cookie':
            "CURRENT_FNVAL=4048; _uuid=A98EDDDE-97AD-9B1D-4A9E-D35794CAA3C195042infoc; buvid3=953F426F-EDBD-2CF4-2C03-0ACE2C1E019793357infoc; b_nut=1715172893; buvid4=A7824B70-B33F-6FD9-9C16-B780F2B088B294499-024050812-RUDu0o7X%2ByJJGXIbhNqw5g%3D%3D; buvid_fp=5d4be1b4d3dabe82569d550b2bc8548d; rpdid=|(JYlmJ)kYl|0J'u~ulu~k)ml; DedeUserID=3546390942714607; DedeUserID__ckMd5=524a7482d6b4d365; b_lsid=2610DF876_18FDB96143D; bsource=search_bing; enable_web_push=DISABLE; header_theme_version=CLOSE; home_feed_column=5; browser_resolution=1487-838; SESSDATA=399f8389%2C1732927999%2Cf3ddf%2A61CjDgOAY3VGmOJVKky3SjjB2dbHLB8BkCSVGFumN2QOIl5t4A-LuA0l_fHbSJ9KQDEXASVlc0aWNHS0lidDVvX1YwcnZZS0FIVGdvLWxnLUFtZ1Z3Vk1KMlBRZnNYY2l4WmVET1FKTkRMUFBYc0lEMU0za0FMWnl5QjhrWEVfd211dXJRNkxYM2hBIIEC; bili_jct=b03d0f285ac09f119b273d6d338cde3c; sid=g7tfgt8s; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTc2MzUyMDUsImlhdCI6MTcxNzM3NTk0NSwicGx0IjotMX0.8CXOns8QHJuM91oksd0frsL8CR4YLMNy2-IcJ1JRRyA; bili_ticket_expires=1717635145",
        'Referer': "https://www.bilibili.com/v/popular/rank/all/",
        'origin': "https://www.bilibili.com"
    }
    aidAndbvid = []
    try:
        # 发送GET请求
        response = requests.get(url,headers=headers)

        # 检查响应状态码
        if response.status_code == 200:
            print("请求成功！")
            text = response.text

            data = json.loads(text)

            for key,value in data.items():
                if key == "data":
                    # print(value["list"])
                    for k in value["list"]:
                        tmp = {
                            "aid":k["aid"],
                            "bvid": k["bvid"],
                            "title": k["title"],
                            "duration": k["duration"],
                            "ctime": k["ctime"],
                            "view": k["stat"]["view"],
                            "coin": k["stat"]["coin"],
                            "favorite": k["stat"]["favorite"],  # 收藏
                            "like": k["stat"]["like"]
                        }
                        aidAndbvid.append(tmp)
                        # print(k["aid"])
                        # print(k["bvid"])
                    return aidAndbvid

        else:
            print(f"请求失败，状态码：{response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"发生错误：{e}")
    # 使用示例

def bubble_sort_map(m):
    n = len(m)
    for i in range(n):
        for j in range(0,n-i-1):
            if m[j]["view"] > m[j+1]["view"]:
                m[j],m[j+1] = m[j+1],m[j]
    print(m)

def create_list(data):
    js = json.dumps(data)
    with open("Day2_1.json","a") as f:
        f.write(js + '\r\n')

# arr = [9,7,2,4,5,1,8]
# bubble_sort(arr)
# print(arr)

data=send_get_request('https://api.bilibili.com/x/web-interface/popular/precious?page_size=100&page=1&web_location=333.934&w_rid=3958c471841e5a04c2f49cbf70fc9b3f&wts=1717379441')
bubble_sort_map(data)
print(data[:10])
for detail in data[:10]:
    print(detail["view"])

create_list(data)
# print(data[:3])
# bubble_sort_map(data)
# print(data[:3])