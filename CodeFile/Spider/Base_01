import urllib.request
import requests

for num in range(0,3):
    url = f"http://www.1ppt.com/moban/ppt_moban_{num}.html"
# response = urllib.request.Request(url)
# print(response)
    response = requests.get(url)
    # print(response.status_code)
    if response.ok:
        print(f"第{num}页的网页源代码是\n",response.text)
    else:
        print("ERROR!")
