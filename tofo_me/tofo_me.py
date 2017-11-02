import re
from concurrent import futures

import requests
from fake_useragent import UserAgent
from parsel import Selector


def parse_page_json(max_id, name):
    ua = UserAgent()
    url = 'http://tofo.me/api/GetUserProfile?'
    data = {
        "username": name,
        "max_id": max_id
    }
    headers = {
        'Referer': 'http://tofo.me/%s'%(name),
        'Origin': 'http: // tofo.me',
        'Host': 'tofo.me',
        'User-Agent': ua.random
    }
    html = requests.post(url, headers=headers, params=data).json()
    # print(len(html['Data']))
    if html['Data']!="null":
        user = html['Data']['user']
        if user:
            nodes = user['media']['nodes']
            for i in nodes:
                print(i['display_src'])
    print(name)
    print('---------------------------------------------')


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
    max_id = result.group(1)
    tree = Selector(text=html)
    imgs = tree.xpath('//div[@class="rc-autoresponsive-container"]/div/img/@src').extract()
    for i in imgs:
        print(i)
    print('开始')
    parse_page_json(max_id,user_name)

def get_users(api):
    ua = UserAgent()
    headers = {
        'Referer': 'http://tofo.me/',
        'Host': 'tofo.me',
        'User-Agent': ua.random
    }
    url = "http://tofo.me/%s" % (api)
    html = requests.get(url, headers=headers).text
    tree = Selector(text=html)
    names = tree.xpath('//div[@class="description"]/div/a/@href').extract()
    users_name = []
    for i in names:
        if '/tag/' not in i:
            if i not in users_name:
                users_name.append(i.replace(r'/', ''))
    print(users_name)
    return users_name

if __name__ == '__main__':

    api = 'korean_cutegirls'
    users_list = get_users(api)
    with futures.ProcessPoolExecutor(max_workers=5) as executor:
        executor_dict = dict((executor.submit(get_img, user_name), user_name) for user_name in users_list)