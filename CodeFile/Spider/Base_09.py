import requests
import json

if __name__ == '__main__':
    url = 'https://fanyi.sogou.com/reventondc/suggV3'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    word = input('请输入单词：')
    data = {
        'from': 'auto',
        'to': 'zh-CHS',
        'client': 'web',
        'text': word,
        'uuid': 'c9d5a528-c056-4955-aa8a-5fcc87d1f535',
        'pid': 'sogou-dict-vr',
        'addSugg': 'on',
    }
    response = requests.post(url=url, data=data, headers=headers)
    dic_obj = response.json()
    # json.loads：json-dict
    # json.dump()dict-json
    rs = ''
    for i in dic_obj['sugg']:
        rs += i['k'] + ":" + i['v'] + '\n'
    print(rs)

    filename = word + '.json'
    fp = open(filename, 'w', encoding='utf-8')
    json.dump(dic_obj, fp=fp, ensure_ascii=False)
    print('已保存！')