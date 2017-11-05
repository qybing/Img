import re
import os

import urllib
import urllib.request

import requests
from concurrent import futures
from fake_useragent import UserAgent
from parsel import Selector


def judge_describe(describe):                   #判断描述是否为韩语
    re_words = re.compile(u"[\uac00-\ud7ff]+")
    result = re.findall(re_words, describe)
    return result



def get_more_pages(max_id,n,user_lists):            #使用递归的方式来获取每个用户名字，其中max_id为构建下一页的参数，N为页数，user_lists为满足条件的用户名
    if n>2:
        # print(user_lists)
        return user_lists
    else:
        ua = UserAgent()
        url = 'http://tofo.me/api/GetUserProfile?'
        data = {
            "username": "home",
            "max_id": max_id
        }
        headers = {
            'Referer': 'http://tofo.me/',
            'Host': 'tofo.me',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent':ua.random
        }
        print('第{}页'.format(n))
        html = requests.post(url, headers=headers, params=data).json()
        if html['Data']!="null":
            user = html['Data']['user']
            if user:
                nodes = user['media']['nodes']
                for i in nodes:
                    describe = ''.join(i['caption'].split('\n'))    #拿到用户的对图片的描述
                    result = judge_describe(describe)               #判断描述为韩语
                    if result:
                        user_lists.append(i['owner']['username'])       #如果为韩语则加入用户列表中
                        # print(i['owner']['username']+'      '+describe)
                page_info = user['media']['page_info']
                if page_info['end_cursor']:
                    n = n + 1
                    # return user_lists
                    return get_more_pages(page_info['end_cursor'],n,user_lists)
        # print('---------------------------------------------')

# def get_more_img(name, id):
#     ua = UserAgent()
#     url = 'http://tofo.me/api/GetUserProfile?'
#     data = {
#         "username": name,
#         "max_id": id
#     }
#     headers = {
#         'Referer': 'http://tofo.me/%s' % (name),
#         'Origin': 'http: // tofo.me',
#         'Host': 'tofo.me',
#         'User-Agent': ua.random
#     }
#     html = requests.post(url, headers=headers, params=data).json()
#     if html['Data'] != "null":
#         user = html['Data']['user']
#         if user:
#             nodes = user['media']['nodes']
#             for i in nodes:
#                 print(i['display_src'])

def get_first_users():                  #首次访问静态页面，拿到一些静态页面的一些图片，然后再找出参数构建异步加载的网页
    ua = UserAgent()
    headers = {
        'Host': 'tofo.me',
        'User-Agent': ua.random,
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    url = "http://tofo.me/"
    html = requests.get(url, headers=headers).text
    pattern1 = re.compile('"owner":{"username":"(.*?)","full_name".*?"caption":"(.*?)",',re.S)
    result1 = re.findall(pattern1,html)
    user_lists = []
    print('第1页')
    for i in result1:
        describe = i[1].replace(r'\n', '').replace(r'\u', '')
        result = judge_describe(describe)
        if result:
            user_lists.append(i[0])
            # print(i[0]+"    "+describe)
    pattern = re.compile('"end_cursor":"(.*?)","has_next_page"', re.S)
    result = re.search(pattern, html)
    max_id = result.group(1)
    return get_more_pages(max_id,2,user_lists)

def get_img(user_name):
    ua = UserAgent()
    headers = {
        'Referer': 'http://tofo.me/',
        'Host': 'tofo.me',
        'User-Agent': ua.random
    }
    url = "http://tofo.me/%s"%(user_name)
    html = requests.get(url,headers=headers).text
    pattern = re.compile('"end_cursor":"(.*?)",', re.S)
    result = re.search(pattern, html)
    # max_id = result.group(1)
    tree = Selector(text=html)
    imgs = tree.xpath('//div[@class="rc-autoresponsive-container"]/div/img/@src').extract()
    img_urls = []
    for i in imgs:
        img_urls.append(i)
    img_urls.append(user_name)
    make_dir(user_name,img_urls)

def make_dir(name, urls):           #创建文件夹
    path = name
    os.makedirs(os.path.join("F:\\tofo", path))  ##创建一个存放套图的文件夹
    os.chdir("F:\\tofo\\" + path)
    with futures.ThreadPoolExecutor(max_workers=5) as executor:         #多线程的方式下载图片
                executor.submit(down_img, urls)                         #down_img为函数，urls为一个用户下的所有图片的列表

def down_img(urls):
        name = urls[-9:-4]
        request = urllib.request.Request(urls)
        response = urllib.request.urlopen(request)
        get_image = response.read()
        f = open(name + '.jpg', 'ab')  ##写入多媒体文件必须要 b 这个参数！！必须要！！
        f.write(get_image)  ##多媒体文件要是用conctent哦！
        f.close()
        print('图集下载中')

if __name__ == '__main__':
    users_list = get_first_users()
    print('满足要求所有的用户',users_list)
    # user_lists = get_img(users_list)
    with futures.ProcessPoolExecutor(max_workers=5) as executor:
        executor_dict = dict((executor.submit(get_img, user_name), user_name) for user_name in users_list)