from news_crawler_frame import NewsCrawler
import time
from random import randint
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup


class Ctee(NewsCrawler):
    def __init__(self):
        super().__init__()

        self.__header = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-TW,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "referer": "https://ctee.com.tw/livenews/aj",
            "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Microsoft Edge";v="96"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": ""
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

        while True:
            url = 'https://ctee.com.tw/livenews/aj/page/{}'
            print(url.format(page))

            self.__header["user-agent"] = UserAgent().random

            rq = requests.get(url.format(page), headers=self.__header)

            time.sleep(0.7+randint(10, 20)/20)

            ###########################################################################
            bs = BeautifulSoup(rq.content.decode('utf-8'), 'lxml')
            contents = bs.select('.item-content')
            for content in contents:
                temp = content.select('a')[-1]

                title = temp.text

                pub_dateAndTime = temp.span.text

                title = title.replace(pub_dateAndTime, ' ').replace(
                    '\n', '').replace(' ', '')

                pub_time = pub_dateAndTime.split(' ')[-1].replace(':', '')+"00"

                link = temp['href']

                newsID = link.split('/')[-1]
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
        #####################################################
        for data in datas:
            ######################################################
            print(data[-1])
            self.__header["user-agent"] = UserAgent().random

            rq = requests.get(data[-1], headers=self.__header)
            time.sleep(0.7+randint(10, 20)/20)

            soup = BeautifulSoup(rq.content.decode('utf-8'), 'lxml')

            reporter = soup.select('.post-meta-author')[0].text

            pub_date = soup.select(
                ".post-meta-date")[0].text.replace('.', '').replace(' ', '')

            tagStr = ""

            contents = soup.select(
                "div.entry-content.clearfix.single-post-content")[0].text

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

        return [((*rawData[:3], 'ctee', rawData[3], rawData[5], rawData[4], rawData[6]) for rawData in rawDatas),
                (('ctee', rawData[0], rawData[-1]) for rawData in rawDatas)]


if __name__ == '__main__':
    e = Ctee()
    s = e.run()
    print(s)
