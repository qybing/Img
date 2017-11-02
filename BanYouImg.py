from concurrent import futures
import urllib
import urllib.request
import os
import requests
headers = {
        'Host': 'www.bjqlr.com',
        'User-Agent': 'banyou/2.9.2 (iPhone; iOS 10.3.3; Scale/2.00)',
    }

def user_list(page):            #   获取用户列表  page指代是页数，每页的用户列表
    data = {
        'actime':'',
        'latitude':'34.638316',
        'longitude':'112.581185',
        'p':page,
        'sex':'0',
        'token':'58FF111D74D857ACC9F8FDB67456FE72'          #重要的参数
    }
    users_list = "http://www.bjqlr.com/client/user/nearby_user_list.php"
    req = requests.post(url=users_list, headers=headers,data=data).json()
    for li in req['responses']['list']:                 #得到每个用户的信息构建每个用户的url
        persons_details(li['id'],li['nickname'],li['avatar'])

def persons_details(id,name,dp):         #获取每个用户的详细信息
    data = {
        'otherid':id,
        'token':'58FF111D74D857ACC9F8FDB67456FE72'
    }
    person_details = "http://www.bjqlr.com/client/user/get_user_detail.php"
    req = requests.post(url=person_details, headers=headers,data=data).json()
    picture = []
    picture.append(dp)
    for li in req['responses']['imglist']:
        picture.append(li['imgpath'])
    print('名字：{}    头像：{}   电话：{}       图库：{}'.format(name, dp, req['responses']['mobile'], picture))
    download_img(name,picture)

def download_img(name, urls):           #下载用户的所有图集
    path = name
    os.makedirs(os.path.join("F:\\banyou", path))  ##创建一个存放套图的文件夹
    os.chdir("F:\\banyou\\" + path)
    for url in urls:
        name = url[-9:-4]
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        get_image = response.read()
        f = open(name + '.jpg', 'ab')  ##写入多媒体文件必须要 b 这个参数！！必须要！！
        f.write(get_image)  ##多媒体文件要是用conctent哦！
        f.close()
    print('用户名：{}   图集下载完毕'.format(path))

if __name__ == '__main__':
    page = 1        ##填写需要下载的页数
    with futures.ProcessPoolExecutor(max_workers=5) as executor:
        executor_dict = dict((executor.submit(user_list, times), times) for times in range(page))
