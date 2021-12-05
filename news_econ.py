from news_crawler_frame import NewsCrawler
import time
from random import randint
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import re


class Econ(NewsCrawler):
    def __init__(self):
        super().__init__()

        self.__header = {
            "accept": "text/plain, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-TW,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "referer": "https://money.udn.com/rank/newest/1001/0/1",
            "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Microsoft Edge";v="96"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "",
            "x-requested-with": "XMLHttpRequest"
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

        pattern_ID = re.compile(
            '.*/story/(\d+)/(.*)\?from=edn_newestlist_rank')
        while True:
            url = 'https://money.udn.com/rank/ajax_newest/1001/0/{}'
            print(url.format(page))

            self.__header["user-agent"] = UserAgent().random

            rq = requests.get(url.format(page), headers=self.__header)

            time.sleep(0.7+randint(10, 20)/20)

            bs = BeautifulSoup(rq.content.decode('utf-8'), 'lxml')
            contents = bs.select('.story-headline-wrapper')
            for content in contents:
                title = content.select('.story__headline')[
                    0].text.replace(' ', '').replace('\n', '').replace('\t', '')

                link = content.a['href']

                newsID = "econ" + ''.join(re.findall(pattern_ID, link)[0])
                nn += 1

                datas.append((newsID, title, link))
            page += 1

            if page == 3:
                break
        # pprint(datas)
        # [(news_id、標題、連結)...]
        return datas

    def __AllContent(self, datas):
        '''
        datas [(news_id、標題、連結)...]
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

            dateAndTime = soup.select(".article-body__time")[0].text.split(' ')
            pub_date = dateAndTime[0].replace('/', '')
            pub_time = dateAndTime[1].replace(':', '')
            if len(pub_time) == 4:
                pub_time = f"{pub_time}00"

            tags = soup.select(
                "#story > div > div.article-bottom > div > section > div > section.article-keyword > ul > li")
            tagStr = []
            for tag in tags:
                try:
                    tagStr.append(tag.a.text)
                except:
                    pass
            if tagStr == []:
                tagStr = ""
            else:
                tagStr = " ".join(list(set(tagStr)))

            reporters = soup.select(
                ".article-body__info")[0].text.replace('\n', '')
            # reporterStr = " ".join([reporter.text for reporter in reporters])

            contents = soup.select("#article_body")[0].text
            # contentStr = " ".join([content.text for content in contents])

            result.append((data[0], pub_date, pub_time,
                          *data[1:], reporters, contents, tagStr))

        return result

    def transform(self, rawDatas):
        '''
        rawDatas [(news_id、日期、時間、標題、連結、記者、內文、tag)...]  連結、記者要換位置
        rerturn [((news_id、date、time、source、title、reporter、link、content)...)、
                 ((source、news_id(FK)、tag)...)]
        '''

        return [((*rawData[:3], 'econ', rawData[3], rawData[5], rawData[4], rawData[6]) for rawData in rawDatas),
                (('econ', rawData[0], rawData[-1]) for rawData in rawDatas)]


if __name__ == '__main__':
    e = Econ()
    s = e.run()
    print(s)
