import re
import time
from wsgiref import headers
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils import get_soup
from db_connection import get_db_connection
from companies import main as send_data
from company_name_stub import add_company_name


def get_data(soup):
    try:
        #получаем заголовок новости
        soup_news = soup.findAll("div", {'class': 'col-sm-8 col-lg-9 pull-left card'}, limit=5)
        text_news = []
        text_news.append(soup_news[0].h3.text)
        text_news.append(soup_news[1].h3.text)
        
        #аннотация новости
        annotation_news = []
        annotation_news.append(soup_news[0].p.text)
        annotation_news.append(soup_news[1].p.text)
        
        text_news_split = [text.split("ET") for text in text_news]
        text_news = [t.replace("\n", "") for text in text_news_split for t in text]

        
        #заглушка для добавления названия компании в текст новости
        text_news[1] = add_company_name(text_news[1])
        print(f'Спарсенная новость для сравнения {text_news[1]}')

        return [[text_news[1]], [text_news[0]], [annotation_news[0]]]
    except:
        print("Некоторые проблемы с парсингом prnewswire")


def initial_old_news():
    #последняя новость данного источника в бд
    try:
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("select \"header\" from news_news WHERE source = 'prnewswire.com' order by id desc LIMIT 1")
        rows = cur.fetchall()
        con.close()
        return rows[0][0]

    except:
        return ''


def delete_quote(data):
    #удаление апострофов и кавычек, чтобы запрос в бд отработал корректно
    new_data = ['', '']
    for j in range(1):
        for i in range(len(data[j])):
            if data[j][i] == '"' or data[j][i] == "'":
                continue
            else:
                new_data[j] += data[j][i]
    return new_data


def check_time_and_actual(data, OLD_TITLE):
    result = []
    # если новость уже есть в бд
    
    if (data[0][0] == OLD_TITLE):
        print('Новость есть в бд')
        return [False]
    
    print('Новости нет в бд')
    return [True]


def get_date_and_time(data):
    #конвертируем дату и время для записи в бд
    time = [d.replace(' ', '') for d in data[1]]
    print(time)
    for i in range(len(time)):
        x = time[i][0:2]
        print(x)
        if (x == '0:'):
            time[i] = "07:" + time[i][2:]
            continue
        if (x[0] == '0'):
            x = int(x[1])
            x += 7
            if (x < 10):
                x = '0' + str(x)
        else:
            print(x)
            x = int(x) + 7
            if (x >= 24):
                x -= 24
                if (x < 10):
                    x = '0' + str(x)
        time[i] = str(x) + time[i][2:]
    return time


def bd_write(data, flag, time):
    try:
        con = get_db_connection()
        cur = con.cursor()

        time[0] = time[0] + ":00"
        time_object_0 = datetime.strptime(time[0], "%H:%M:%S").time()

        now = datetime.now()
        date_string = now.strftime('%Y-%m-%d')

        date_0 = date_string + ' ' + str(time_object_0)

        print(data[0][0])
        # загрузка второй по свежести новости
        # if (flag[1]):
        #     stroka = "insert into news_news (header, annotation, date, source) values (\'" + data[0][1] + "\', \'" + \
        #              data[2][1] + "\', \'" + date_1 + "\', \'prnewswire.com\')"
        #     cur.execute(stroka)
        # загрузка самой свежей новости
        if (flag[0]):
            stroka = "insert into news_news (header, annotation, date, source) values (\'" + data[0][0] + "\', \'" + \
                     data[2][0] + "\', \'" + date_0 + "\', \'prnewswire.com\')"
            cur.execute(stroka)

        con.commit()

        con.close()
    except:
        print('error to connect to bd (prnewswire)')
        
        con.close()


def one_cicle():
    print('\n\nпарсинг prnewswire.com')
    
    OLD_TITLE = initial_old_news()  # последняя новость, добавленная в базу данных
    
    print(f'Старая новость {OLD_TITLE}')
    
    soup = get_soup('https://www.prnewswire.com/news-releases/news-releases-list/')  # получение текста сайта
    data = get_data(soup)  # получение названий статей и дат публикации.

    data[0] = delete_quote(data[0])  # удаление кавычек и апострофов в новости
    data[2] = delete_quote(data[2])  # удаление кавычек и апострофов в аннотации

    flag = check_time_and_actual(data, OLD_TITLE)  # [свежая новость, вторая новость] - проверка данных на актуальность.
    
    time = get_date_and_time(data)  # конвертация строки даты для записи в бд
    
    
    
    bd_write(data, flag, time)  # запись данных в бд.
    
    if(flag[0]):
        send_data(data[0][0], data[2][0], 'prnewswire.com')
    
    # send_data(data[0][1], data[2][1])
    


