import requests
headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}
response = requests.get("http://movie.douban.com/top250",headers=headers)
print(response) #打印出来是一个Response对象，并且紧跟HTTP状态码
print(response.text)
