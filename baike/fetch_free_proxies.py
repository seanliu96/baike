#coding:utf-8

from bs4 import BeautifulSoup
import requests
import logging

logger = logging.getLogger(__name__)

def get_html(url):
    request = requests.get(url)
    if request.encoding == 'ISO-8859-1':
        request.encoding = 'utf-8'
    return request.text

def get_soup(url):
    soup = BeautifulSoup(get_html(url), 'lxml')
    return soup

def fetch_kxdaili(page):
    """
    从www.kxdaili.com抓取免费代理
    """
    proxies = []
    try:
        url = 'http://www.kxdaili.com/dailiip/1/%d.html' % page
        soup = get_soup(url)
        table_tag = soup.find('table', attrs={'class': 'ui table segment'})
        trs = table_tag.tbody.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            ip = tds[0].text
            port = tds[1].text
            latency = tds[4].text.split()[0]
            if float(latency) < 0.5:
                proxy = '%s:%s' % (ip, port)
                proxies.append(proxy)
    except BaseException as e:
        logger.warning('fail to fetch from kxdaili')
    return proxies

def img2port(img_url):
    """
    mimvp.com的端口号用图片来显示, 本函数将图片url转为端口, 目前的临时性方法并不准确
    """
    code = img_url.split('=')[-1]
    if code.find('AO0OO0O') > 0:
        return 80
    else:
        return None

def fetch_mimvp():
    """
    从http://proxy.mimvp.com/free.php抓免费代理
    """
    proxies = []
    try:
        url = 'http://proxy.mimvp.com/free.php?proxy=in_hp'
        soup = get_soup(url)
        table_tag = soup.find('table', attrs={'class': 'table table-bordered table-striped'})
        tds = table_tag.tbody.find_all('td')
        for i in range(0, len(tds), 10):
            ip = tds[i+1].text
            port = img2port(tds[i+2].img['src'])
            response_time = tds[i+7]['title'][:-1]
            if port and float(response_time) < 0.5:
                proxy = '%s:%s' % (ip, port)
                proxies.append(proxy)
    except BaseException as e:
        logger.warning('fail to fetch from mimvp')
    return proxies

def fetch_xici():
    """
    http://www.xicidaili.com/nn/
    """
    proxies = []
    try:
        url = 'http://www.xicidaili.com/nn/'
        soup = get_soup(url)
        table = soup.find('table', attrs={'id': 'ip_list'})
        trs = table.find_all('tr')
        for i in range(1, len(trs)):
            tds = trs[i].find_all('id')
            ip = tds[1].text
            port = tds[2].text
            speed = tds[6].div['title'][:-1].replace('秒', '')
            latency = tds[7].div['title'][:-1].replace('秒', '')
            if float(speed) < 3 and float(latency) < 0.5:
                proxy = '%s:%s' % (ip, port)
                proxies.append(proxy)
    except BaseException as e:
        logger.warning('fail to fetch from mimvp')
    return proxies

def fetch_ip181():
    """
    http://www.ip181.com/
    """
    proxies = []
    try:
        url = 'http://www.ip181.com/'
        soup = get_soup(url)
        table = soup.find('table', attrs={'class': 'table table-hover panel-default panel ctable'})
        trs = table.find_all('tr')
        for i in range(1, len(trs)):
            tds = trs[i].find_all('td')
            ip = tds[0].text
            port = tds[1].text
            latency = tds[4].text[:-2].split()[0]
            if float(latency) < 0.5:
                proxy = '%s:%s' % (ip, port)
                proxies.append(proxy)
    except BaseException as e:
        logger.warning('fail to fetch from mimvp')
    return proxies

def fetch_httpdaili():
    """
    http://www.httpdaili.com/mfdl/
    更新比较频繁
    """
    url = 'http://www.httpdaili.com/mfdl/'
    proxies = []
    try:
        url = 'http://www.httpdaili.com/mfdl/'
        soup = get_soup(url)
        table = soup.find("div", attrs={"kb-item-wrap11"}).table
        trs = table.find_all('tr')
        for i in range(1, len(trs)):
            tds = trs[i].find_all('td')
            ip = tds[0].text
            port = tds[1].text
            if tds[2].text == '匿名':
                proxy = '%s:%s' % (ip, port)
                proxies.append(proxy)
    except BaseException as e:
        logger.warning('fail to fetch from mimvp')
    return proxies

def check(proxy):
    url = 'https://baike.baidu.com/'
    try:
        request = requests.get(url, proxies={'http': 'http://%s' % proxy}, timeout=1)
        return request.ok
    except BaseException as e:
        # print(e)
        return False;

def fetch_all(endpage=10):
    proxies = []
    for i in range(1, endpage):
        proxies += fetch_kxdaili(i)
    proxies += fetch_mimvp()
    proxies += fetch_xici()
    proxies += fetch_ip181()
    proxies += fetch_httpdaili()
    valid_proxies = []
    logger.info('checking proxies validation')
    for proxy in proxies:
        print(proxy)
        if check(proxy):
            valid_proxies.append(proxy)
    return valid_proxies

if __name__ == '__main__':
    import sys
    root_logger = logging.getLogger('')
    stream_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(name)-8s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    proxies = fetch_all(10)
    with open('../proxies.dat', 'w') as f:
        for proxy in proxies:
            print(proxy)
            f.write(proxy+'\n')
