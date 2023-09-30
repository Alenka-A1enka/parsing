import re
import time
from wsgiref import headers
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils import get_soup
from db_connection import get_db_connection
from companies import main as send_data


def get_data(soup):
    try:
        #парсинг заголовка
        soup_news = soup.findAll("h3",{'class':'Mb(5px)'})
        text_news = soup_news[0].text
        
        
        #парсинг аннотации                                
        soup_news = soup.findAll("p",{'class':'Fz(14px) Lh(19px) Fz(13px)--sm1024 Lh(17px)--sm1024 LineClamp(2,38px) LineClamp(2,34px)--sm1024 M(0)'})
        annotation = soup_news[0].text
        
        #время выхода новости
        # soup_time = soup.findAll("div",{'class':'C(#959595) Fz(11px) D(ib) Mb(6px)'})
        # time = soup_time[0].text

        return [text_news, annotation]
    except:
        print("Возникли некоторые проблемы при парсинге сайта yahoo")
    

def initial_old_news():
    try:
        con = get_db_connection()
        cur = con.cursor()  
        cur.execute("select \"header\" from news_news WHERE source = 'yahoo.com' order by id desc LIMIT 1")
        rows = cur.fetchall()
        con.close()
        return rows[0][0]
        
    except:
        return ''


def delete_quote(data):
    new_data = ''
    for i in range(len(data)):
        if data[i] == '"' or data[i] == "'":
            continue
        else:
            new_data += data[i]
    return new_data

def check_time_and_actual(data, OLD_TITLE):
    #если новость уже есть в бд
    if(data[0] == OLD_TITLE):
        return False
    else:
        return True

def get_date_and_time(data):
    now = datetime.now()
    time = now.strftime("%H:%M")
    return time


def bd_write(data, flag, time):
    try:
        con = get_db_connection()
        cur = con.cursor()
        
        time += ":00"
        time_object = datetime.strptime(time, "%H:%M:%S").time()
       
        now = datetime.now()
        date_string = now.strftime('%Y-%m-%d')

        date_1 = date_string + ' ' + str(time_object)
        print(date_1)
       
        #загрузка самой свежей новости
        if(flag):
            stroka = "insert into news_news (header, annotation, date, source) values (\'" + data[0] + "\', \'" + \
                     data[1] + "\', \'" + date_1 + "\', \'yahoo.com\')"
            cur.execute(stroka)

        con.commit()  

        con.close()
    except:
        print('ошибка при добавлении в базу данных')
        con.close()


def one_cicle():
    print('\n\nпарсинг yahoo.com')
    
    OLD_TITLE = initial_old_news() #последняя новость, добавленная в базу данных
    print(OLD_TITLE)
    soup = get_soup('https://finance.yahoo.com/topic/stock-market-news/') #получение текста сайта
    data = get_data(soup) #получение названий статей и дат публикации.
    
    print(data)
    try: 
        data[0] = delete_quote(data[0]) #удаление кавычек и апострофов в новости
        data[1] = delete_quote(data[1]) #удаление кавычек и апострофов в аннтоции
        
        flag = check_time_and_actual(data, OLD_TITLE) #проверка данных на актуальность.
        time = get_date_and_time(data) #получение времени выхода статьи
        
        
        bd_write(data, flag, time) #запись данных в бд.
        if(flag):
            send_data(data[0], data[1], 'yahoo.com')
    except: 
        print('не удалось удалить ковычки в новости')
    




