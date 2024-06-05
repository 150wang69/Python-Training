# 导入需要的模块
import urllib.request  # 导入 urllib.request 模块用于发送 HTTP 请求
from bs4 import BeautifulSoup  # 导入 BeautifulSoup 模块用于解析 HTML 内容
import ssl  # 导入 ssl 模块用于处理 HTTPS 请求

ssl._create_default_https_context = ssl._create_unverified_context  # 忽略 HTTPS 证书验证


# 定义函数 getURL，用于获取指定 URL 的页面内容
def getURL(url):
    """
    获取指定 URL 的页面内容

    参数:
    url (str): 要获取页面内容的 URL 地址

    返回:
    bytes: 页面内容的字节形式，如果获取失败则返回 None
    """
    try:
        response = urllib.request.urlopen(url)  # 发送 HTTP 请求获取页面内容
        if response.status == 200:  # 如果响应状态码为 200，表示请求成功
            return response.read()  # 返回页面内容的字节形式
        else:
            print("Failed to fetch URL:", url)  # 如果请求失败，则打印错误信息
            return None  # 返回 None 表示获取失败
    except Exception as e:  # 捕获异常
        print("Exception occurred while fetching URL:", e)  # 打印异常信息
        return None  # 返回 None 表示获取失败


# 定义函数 ResolveHTML，用于解析 HTML 内容，提取学院动态模块的信息
def ResolveHTML(content):
    """
    解析 HTML 内容，提取学院动态模块的信息

    参数:
    content (bytes): HTML 页面内容的字节形式

    返回:
    list: 包含提取信息的列表，每个元素为一个元组(department, url, title)
    """
    try:
        soup = BeautifulSoup(content, 'html.parser')  # 使用 BeautifulSoup 解析 HTML 内容
        lists = soup.find_all('li', id=lambda x: x and x.startswith('line_u8_'))  # 查找所有 id 属性以 'line_u8_' 开头的 li 标签
        if not lists:  # 如果列表为空，表示未找到符合条件的内容
            print("Could not find...")  # 打印未找到内容的提示信息
            return []  # 返回空列表
        info_list = []  # 创建空列表，用于存储提取的信息
        for item in lists:  # 遍历每个找到的 li 标签
            department = item.find('a')  # 查找包含院系信息的 a 标签
            if department:  # 如果找到了院系信息
                department = department.text.split()[0].strip('[]')  # 获取并清理院系信息的文本
            else:  # 如果未找到院系信息
                print("错误！")  # 打印错误信息
            title = item.find('a').text.split()[1]  # 获取标题信息
            url = item.find('a')['href']  # 获取 URL 地址信息
            info_list.append((department, url, title))  # 将信息添加到列表中
            print(department, title, url)  # 打印提取的信息
        return info_list  # 返回包含提取信息的列表
    except Exception as e:  # 捕获异常
        print(f"解析 HTML 出错：{e}")  # 打印异常信息
        return []  # 返回空列表表示解析失败


# 定义函数 saveInfo，用于将信息保存到文件中
def saveInfo(info_list, filename):
    """
    将信息保存到文件中

    参数:
    info_list (list): 包含信息的列表，每个元素为一个元组(department, url, title)
    filename (str): 要保存信息的文件名
    """
    print("Info list:", info_list)  # 打印信息列表，用于确认其是否存在
    print("Info list length:", len(info_list))  # 打印信息列表的长度，用于确认是否为空
    try:
        with open(filename, 'w', encoding='utf-8') as file:  # 打开文件，准备写入信息
            for info in info_list:  # 遍历信息列表中的每个元素
                file.write(','.join(info) + '\n')  # 将元素转换为字符串并写入文件，以逗号分隔
                print("Info saved to file:", ','.join(info))  # 打印保存的信息
        print("Information saved to", filename)  # 打印保存成功的提示信息
    except Exception as e:  # 捕获异常
        print("Exception occurred while saving info:", e)  # 打印异常信息


# 定义主函数 main，用于执行整个程序的流程
def main():
    """
    主函数，执行整个程序的流程
    """
    url = "https://www.hist.edu.cn/index/sy/xydt.htm"  # 定义要获取页面内容的 URL 地址
    content = getURL(url)  # 获取指定 URL 的页面内容
    if content:  # 如果获取页面内容成功
        info_list = ResolveHTML(content)  # 解析 HTML 内容，提取学院动态信息
        try:
            saveInfo(info_list, "xueyuandongtai.txt")  # 将提取的信息保存到文件中
            print("After calling saveInfo function")  # 打印调用 saveInfo 函数后的信息，用于调试
        except Exception as e:  # 捕获异常
            print("Exception occurred:", e)  # 打印异常信息


# 如果当前脚本为主程序，则执行主函数 main
if __name__ == "__main__":
    main()


