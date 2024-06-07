import requests
import json

#这个代码请求成功
def send_get_request(url):
    headers = {
        'User-Agent':
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }
    aidAndbvid = {}
    try:
        # 发送GET请求
        response = requests.get(url,headers=headers)

        # 检查响应状态码
        if response.status_code == 200:
            print("请求成功！")
            # print(response.text)
            text = response.text
            # print(type(text))
            # t = json.dumps(text)
            # with open("Day1_4.json",'w') as f:
            #     f.writelines(t)

            data = json.loads(text)

            for key,value in data.items():
                if key == "data":
                    # print(value["list"])
                    for k in value["list"]:
                        aidAndbvid[k["aid"]] = {
                            "bvid":k["bvid"],
                            "title":k["title"],
                            "duration":k["duration"],
                            "ctime":k["ctime"],
                            "view":k["stat"]["view"],
                            "coin":k["stat"]["coin"],
                            "like":k["stat"]["like"]
                            #TODO 投币、点赞、收藏
                        }
                        # print(k["aid"])
                        # print(k["bvid"])
            print(aidAndbvid)

        else:
            print(f"请求失败，状态码：{response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"发生错误：{e}")
    # 使用示例

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in  range(0,n-i-1):
            if arr[j] < arr[j+1]:
                arr[j],arr[j+1] = arr[j+1],arr[j]

arr = [9,7,2,4,5,1,8]
bubble_sort(arr)
print(arr)

send_get_request("https://api.bilibili.com/x/web-interface/popular/precious?page_size=100&page=1&web_location=333.934&w_rid=3958c471841e5a04c2f49cbf70fc9b3f&wts=1717379441")
