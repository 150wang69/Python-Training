import requests

response = requests.get("http://books.toscrape.com")
print(response.status_code)
if response.ok:
    print(response.text)
else:
    print("请求失败！")
