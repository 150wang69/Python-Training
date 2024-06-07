import requests
import json
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
}
inp = input('请输入要查询的词汇：')
url = 'https://fanyi.baidu.com/sug'
while inp != 'quit':
    post_form = {
        'kw': f'{inp}'
    }
    re = requests.post(url=url, data=post_form, headers=headers)
    s = json.loads(re.text)
    print(s['data'][0]['v'])
    inp = input('请输入要查询的词汇：')
print('已成功退出')