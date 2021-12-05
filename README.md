# newsCrawler
財經新聞網爬蟲：鉅亨(台股-全部)、經濟(即時-最新-總覽)、工商(即時-財經)、MoneyDJ(即時-頭條)\
爬蟲結果將寫入mysql資料庫

### 使用語言
```
Python
```


### 需要額外安裝的模組
```
fake_useragent
requests
pymysql
bs4
```


### 執行前準備
1、建立mysql資料庫，並建立一個名為news的database，再透過db.sql建立table(news_content、news_tag)\
2、修改news_crawler_frame.py，NewsCrawler類別下load方法中的資料庫連線資訊


### 備註
一、各財經新聞網對應的py檔
```
1、鉅亨(台股-全部)：news_anue.py
2、經濟(即時-最新-總覽)：news_econ.py
3、工商(即時-財經)：news_ctee.py
4、MoneyDJ(即時-頭條)：news_modj.py
```
二、執行過程中錯誤詳見log資料夾\
三、UML類別圖(參考)
![UML類別圖 drawio](https://user-images.githubusercontent.com/78075403/144748986-2f931232-7559-425b-9f56-6b954b76dabe.png)
