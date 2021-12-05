from news_crawler_frame import NewsCrawler
import time
from random import randint
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import re


class Modj(NewsCrawler):
    def __init__(self):
        super().__init__()

        self.__header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Connection": "keep-alive",
            "Host": "www.moneydj.com",
            "Referer": "https://www.moneydj.com/kmdj/news/newsreallist.aspx?a=mb010000",
            "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Microsoft Edge";v="96"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "",
        }

    def extract(self, ndaysAgo: int, interval: str) -> list:
        '''
        取得本次區間資料
        ndaysAgo：ndaysAgo的datetime
        interval(default：0600)：str, 一天開始的時間
        return [(news_id、日期、時間、標題、連結、記者、內文、tag)...]
        '''

        # 先取得所有連結
        # allLinks [(news_id、日期、時間、標題、連結)...]
        allLinks = self.__AllLinks(ndaysAgo, interval)

        # 再取得所有內文
        # linkAndContent [(news_id、日期、時間、標題、連結、記者、內文、tag)...]
        linkAndContent = self.__AllContent(allLinks)
        print(len(linkAndContent))
        return linkAndContent

    def __AllLinks(self, twoDaysAgo: int, interval: str):
        '''
        return [(news_id、日期、時間、標題、連結、記者、內文、tag)...]
        '''
        start = f'{twoDaysAgo.year}/{twoDaysAgo.month}/{twoDaysAgo.day} {interval[0:2]}:{interval[2:4]}:00'
        struct_time = time.strptime(start, "%Y/%m/%d %H:%M:%S")  # 轉成時間元組
        start_stamp = int(time.mktime(struct_time))  # 轉成時間戳
        print(start, start_stamp)

        ended = f'{self.timeNow.year}/{self.timeNow.month}/{self.timeNow.day} {interval[0:2]}:{interval[2:4]}:00'
        struct_time = time.strptime(ended, "%Y/%m/%d %H:%M:%S")  # 轉成時間元組
        ended_stamp = int(time.mktime(struct_time))  # 轉成時間戳
        print(ended, ended_stamp)

        datas, page, nn = [], 1, 1

        pattern_time = re.compile('.*(\d{2}):(\d{2})')
        pattern_neID = re.compile('.*a=(.*)&c=.*')
        while True:
            url = 'https://www.moneydj.com/kmdj/news/newsreallist.aspx?index1={}&a=mb010000'
            print(url.format(page))

            self.__header["user-agent"] = UserAgent().random

            rq = requests.get(url.format(page), headers=self.__header)

            time.sleep(0.7+randint(10, 20)/20)

            ###########################################################################
            bs = BeautifulSoup(rq.content.decode('utf-8'), 'lxml')
            contents = bs.select('#MainContent_Contents_sl_gvList')[
                0].select('tr')
            for content in contents:
                temp = content.select('td')
                if temp == []:
                    continue

                title = temp[1].text.replace('\n', '')

                pub_dateAndTime = temp[0].text.replace(
                    '\r', '').replace('\n', '').replace(' ', '')

                pub_time = ''.join(re.findall(
                    pattern_time, pub_dateAndTime)[0]) + "00"

                link = "https://www.moneydj.com" + \
                    temp[1].select('a')[0]['href']

                newsID = re.findall(pattern_neID, link)
                nn += 1

                datas.append((newsID, pub_time, title, link))
            ###########################################################################
            page += 1

            if page == 3:
                break
        # pprint(datas)
        # [(news_id、時間、標題、連結)...]
        return datas

    def __AllContent(self, datas):
        '''
        datas [(news_id、時間、標題、連結)...]
        return [(news_id、日期、時間、標題、連結、記者、內文、tag)...]
        '''
        result = []
        pattern = re.compile('.*記者(.*)報導')
        #####################################################
        for data in datas:
            ######################################################
            print(data[-1])
            self.__header["user-agent"] = UserAgent().random

            rq = requests.get(data[-1], headers=self.__header)
            time.sleep(0.7+randint(10, 20)/20)

            soup = BeautifulSoup(rq.content.decode('utf-8'), 'lxml')

            reporter = soup.select(
                '#highlight > article > p:nth-child(2)')[0].text

            pub_date = soup.select(
                "#MainContent_Contents_lbDate")[0].text.split(' ')[0].replace('/', '')

            tagStr = ""

            contents = soup.select("#highlight > article")[
                0].text.replace(reporter, '')

            reporter = re.findall(pattern, reporter)[0].replace(' ', '')

            result.append((data[0], pub_date, *data[1:],
                          reporter, contents, tagStr))

        # pprint(result)
        return result

    def transform(self, rawDatas):
        '''
        rawDatas [(news_id、日期、時間、標題、連結、記者、內文、tag)...]  連結、記者要換位置
        rerturn [((news_id、date、time、source、title、reporter、link、content)...)、
                 ((source、news_id(FK)、tag)...)]
        '''

        return [((*rawData[:3], 'modj', rawData[3], rawData[5], rawData[4], rawData[6]) for rawData in rawDatas),
                (('modj', rawData[0], rawData[-1]) for rawData in rawDatas)]


if __name__ == '__main__':
    e = Modj()
    s = e.run()
    print(s)
