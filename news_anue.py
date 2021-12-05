from news_crawler_frame import NewsCrawler, NewsCrawlerException
from datetime import datetime
import time
from random import randint
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import json
import re


class Anue(NewsCrawler):
    def __init__(self):
        super().__init__()

        self.__header = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-TW,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "origin": "https://news.cnyes.com",
            "referer": "https://news.cnyes.com/",
            "sec-ch-ua": '"Microsoft Edge";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "",
            "x-cnyes-app": "fe-desktop",
            "x-platform": "WEB",
            "x-system-kind": "NEWS_DESKTOP"
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

        datas = []
        page, last_page, nn = 1, 1, 1
        pattern_ID = re.compile('.*\/(.*)\?exp=a.*')
        while page <= last_page:
            # url = 'https://api.cnyes.com/media/api/v1/newslist/all?limit=30&startAt={}&endAt={}&page={}'
            url = 'https://api.cnyes.com/media/api/v1/newslist/category/tw_stock?startAt={}&endAt={}&limit=30&page={}'
            print(url.format(start_stamp, ended_stamp, page))

            self.__header["user-agent"] = UserAgent().random

            rq = requests.get(url.format(start_stamp, ended_stamp, page),
                              headers=self.__header)
            time.sleep(0.7+randint(10, 20)/20)
            js = json.loads(str(rq.text))

            if js['statusCode'] != 200:
                raise NewsCrawlerException(f"from cnyes {js['message']}")
            ########################################
            last_page = js['items']['last_page']
            ###########################################
            page += 1

            temp = js['items']['data']
            # (news_id、日期、時間、標題、連結)
            for i in temp:
                newsDateTime = datetime.fromtimestamp(i['publishAt'])
                newsDate = newsDateTime.strftime("%Y%m%d")
                newsTime = newsDateTime.strftime("%H%M%S")
                link = f"https://news.cnyes.com/news/id/{i['newsId']}?exp=a"

                newsID = 'anue_' + re.findall(pattern_ID, link)[0]
                nn += 1

                datas.append(
                    (newsID, newsDate, newsTime, i['title'], link))

        #  [(news_id、日期、時間、標題、連結)...]
        return datas

    def __AllContent(self, datas):
        '''
        datas [(news_id、日期、時間、標題、連結)...]
        return [(news_id、日期、時間、標題、連結、記者、內文、tag)...]
        '''
        result = []
        #####################################################
        for data in datas:
            ######################################################
            print(data[4])

            self.__header["user-agent"] = UserAgent().random

            rq = requests.get(data[4], headers=self.__header)
            time.sleep(0.7+randint(10, 20)/20)

            soup = BeautifulSoup(rq.content.decode('utf-8'), 'lxml')

            tags = soup.select(
                "#content > div > div > div._2hZZ.theme-app.theme-newsdetail > main > div._1S0A > article > section > nav > a")
            tagStr = " ".join([tag.text for tag in tags])

            reporters = soup.select(
                "#content > div > div > div._2hZZ.theme-app.theme-newsdetail > main > div._uo1n > div._1R6L > span > span")
            reporterStr = " ".join([reporter.text for reporter in reporters])

            contents = soup.select(
                "#content > div > div > div._2hZZ.theme-app.theme-newsdetail > main > div._1S0A > article > section._82F6 > div._1UuP")
            contentStr = " ".join([content.text for content in contents])

            result.append((*data, reporterStr, contentStr, tagStr))

        return result

    def transform(self, rawDatas):
        '''
        rawDatas [(news_id、日期、時間、標題、連結、記者、內文、tag)...]  連結、記者要換位置
        rerturn [((news_id、date、time、source、title、reporter、link、content)...)、
                 ((source、news_id(FK)、tag)...)]
        '''

        return [((*rawData[:3], 'anue', rawData[3], rawData[5], rawData[4], rawData[6]) for rawData in rawDatas),
                (('anue', rawData[0], rawData[-1]) for rawData in rawDatas)]


if __name__ == '__main__':
    a = Anue()
    s = a.run()
    print(s)
