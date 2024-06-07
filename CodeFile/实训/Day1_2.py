import requests

#这个代码请求成功
def send_get_request(url):
    headers = {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    }
    try:
        # 发送GET请求
        response = requests.get(url,headers=headers)

        # 检查响应状态码
        if response.status_code == 200:
            print("请求成功！")
            print(response.text)
        else:
            print(f"请求失败，状态码：{response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"发生错误：{e}")

    # 使用示例


send_get_request('https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all&web_location=333.934&w_rid=10c2d598bc80cc96090c80758d25c44c&wts=1717375819')