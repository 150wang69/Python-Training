import requests

#这个代码请求失败
def send_get_request(url):
    try:
        # 发送GET请求
        response = requests.get(url)

        # 检查响应状态码
        if response.status_code == 200:
            print("请求成功！")
            print(response.text)
        else:
            print(f"请求失败，状态码：{response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"发生错误：{e}")

    # 使用示例


send_get_request(
    'https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all&web_location=333.934&w_rid=10c2d598bc80cc96090c80758d25c44c&wts=1717375819')