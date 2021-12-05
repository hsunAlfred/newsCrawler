from abc import abstractmethod, ABCMeta
from datetime import datetime, timedelta
import traceback
import logging.config
import pymysql


class NewsCrawler(metaclass=ABCMeta):
    def __init__(self):
        self.timeNow = datetime.today()

        logging.config.fileConfig('news_logging.conf')
        self.__logger = logging.getLogger('timeRotateLogger')

        self.alphaDigital = {i[1]: f'{i[0]:9>2}'
                             for i in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}

    def run(self, ndays: int = 1, interval: str = "0600"):
        '''
        ndays(default:1)：int, 最近ndays的的資料
        interval(default：0600)：str, 一天開始的時間

        假設現在是11/10 05:00
        eg. run(ndays=1, interval="0600")
            抓取11/09 06:00 - 11/10 05:00
        eg. run(ndays=2, interval="0000")
            抓取11/08 06:00 - 11/10 05:00

        假設現在是11/10 14:30
        eg. run(ndays=1, interval="0600")
            抓取11/09 06:00 - 11/10 05:59
        eg. run(ndays=2, interval="0000")
            抓取11/08 06:00 - 11/10 05:59
        '''
        ndaysAgo = self.timeNow - timedelta(days=ndays)

        try:
            rawDatas = self.extract(ndaysAgo, interval)
            cleanDatas, cleanTags = self.transform(rawDatas)
            status = self.load(cleanDatas, cleanTags)
            return status
        except Exception as e:
            return self.errLog(e)

    @abstractmethod
    def extract(self, nDaysAgo, interval: str) -> list:
        '''
        取得本次區間資料
        ndaysAgo：ndaysAgo的datetime
        interval(default：0600)：str, 一天開始的時間
        return [(news_id、日期、時間、標題、連結、記者、內文、tag)...]
        '''
        pass

    @abstractmethod
    def transform(self, rawDatas):
        '''
        rawDatas [(news_id、日期、時間、標題、連結、記者、內文、tag)...]  連結、記者要換位置
        rerturn [((news_id、date、time、source、title、reporter、link、content)...)、
                 ((source、news_id(FK)、tag)...)]
        '''
        pass

    def load(self, cleanDatas, cleanTags):
        '''
        cleanDatas -> Generator
        ((news_id、date、time、source、title、reporter、link、content)...)、((news_id(FK)、tag)...)

        存入資料庫
        DB:news
        table1:news_content [(no(PK AI), news_id、date、time、source、title、reporter、link、content)]
        table2:news_tag [no(PK AI)、source、news_id(FK)、tag]
        table3:news_opinion [opinion_id(PK AI)、source、news_id(FK)、opinion]
        '''
        print(type(cleanDatas), type(cleanTags))

        connection = pymysql.connect(host='----db ip address----',
                                     user='----your user name----',
                                     password='----your password----',
                                     database='news',
                                     cursorclass=pymysql.cursors.DictCursor)

        with connection.cursor() as cursor:
            sql = "INSERT INTO news_content (news_id, date, time, source, title, reporter, link, content) " +\
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"

            for c in cleanDatas:
                try:
                    cursor.execute(sql, c)
                except Exception as e:
                    print(e)
        connection.commit()

        with connection.cursor() as cursor:
            sql = "INSERT INTO news_tag (source, news_id, tag) VALUES (%s, %s, %s);"

            for c in cleanTags:
                if c[-1] == "":
                    continue
                try:
                    cursor.execute(sql, c)
                except Exception as e:
                    print(e)
        connection.commit()

        return 'Done'

    def errLog(self, e):
        self.__logger.error(f'{str(e)}\n{traceback.format_exc()}')
        return f'{e}\nDetail: ./log/news_oneMinute.log'


class NewsCrawlerException(Exception):
    def __init__(self, *args) -> None:
        super().__init__(args)
