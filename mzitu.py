import re
import os
import time
import threading
from multiprocessing import Pool, cpu_count
import requests
from bs4 import BeautifulSoup


headers = {'X-Requested-With': 'XMLHttpRequest',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/56.0.2924.87 Safari/537.36'}

def get_urls():
    """
    获取 mzitu 网站下所有套图的 url
    :return: 去重套图 urls set
    """
    page_urls = ['http://www.mzitu.com/page/{cnt}'.format(cnt=str(cnt)) for cnt in range(1, 143)]

    img_urls = []
    for page_url in page_urls:
        try:
            bs = BeautifulSoup(requests.get(page_url, headers=headers, timeout=10).text, 'lxml').find('ul', id="pins")
            result = re.findall(r"(?<=href=)\S+", str(bs))      # 匹配所有 urls
            img_url = [url.replace('"', "") for url in result]
            img_urls.extend(img_url)

        except Exception as e:
            print(e)

    return set(img_urls)


lock = threading.Lock()     # 全局资源锁


def urls_crawler(url):
    """
    爬虫入口，主要爬取操作
    :param url: 套图的地址
    """
    try:
        response = requests.get(url, headers=headers, timeout=10).text
        folder_name = BeautifulSoup(response, 'lxml').find('div', class_="main-image").find('img')['alt'].replace("?", " ")

        with lock:
            if make_dir(folder_name):
                # 套图里图片张数
                max_count = BeautifulSoup(response, 'lxml').find('div', class_='pagenavi').find_all('span')[-2].get_text()
                page_urls = [url + "/" + str(i) for i in range(1, int(max_count) + 1)]

                img_urls = []
                for _, page_url in enumerate(page_urls):
                    result = requests.get(page_url, headers=headers, timeout=10).text
                    img_url = BeautifulSoup(result, 'lxml').find('div', class_="main-image").find('img')['src']
                    img_urls.append(img_url)

                for cnt, url in enumerate(img_urls):
                    save_pic(url, cnt)

    except Exception as e:
        print(e)


def save_pic(pic_src, pic_cnt):
    """
    保存图片到本地
    :param pic_src: 图片地址
    :param pic_cnt: 图片序数
    """
    try:
        img = requests.get(pic_src, headers=headers, timeout=10)
        with open("pic_cnt_" + str(pic_cnt + 1) + '.jpg', 'ab') as f:
            f.write(img.content)
            print("pic_cnt_" + str(pic_cnt + 1) + '.jpg')

    except Exception as e:
        print(e)


def make_dir(folder_name):
    """
    新建文件夹并切换到该目录下
    :param folder_name: 套图名也做文件夹名
    :return: 返回 True 如果文件夹不存在，存在则返回 False
    """
    path = os.path.join(r"E:\mzitu", folder_name)

    # 如果目录已经存在就不用再次爬取了，去重，提高效率
    if not os.path.exists(path):
        os.makedirs(path)
        print(path)
        os.chdir(path)
        return True
    else:
        print("This folder have been created!")
        return False


def delete_empty_dir(dir):
    """ 如果程序半路中断的话，可能存在已经新建好文件夹但是仍没有下载的图片的情况
    但此时文件夹已经存在所以会忽略该套图的下载，此时要删除空文件夹 """

    if os.path.exists(dir):
        if os.path.isdir(dir):
            for d in os.listdir(dir):
                path = os.path.join(dir, d)
                if os.path.isdir(path):
                    delete_empty_dir(path)

        if not os.listdir(dir):
            os.rmdir(dir)
            print("remove the empty dir: " + dir)
    else:
        print("Please start your performance!")


if __name__ == "__main__":

    urls = get_urls()
    pool = Pool(processes=cpu_count())
    try:
        delete_empty_dir(r"E:\mzitu")
        results = pool.map(urls_crawler, urls)
    except Exception as exception:
        time.sleep(30)
        delete_empty_dir(r"E:\mzitu")
        results = pool.map(urls_crawler, urls)
