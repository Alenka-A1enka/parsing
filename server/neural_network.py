from random import randint
from db_connection import get_db_connection

#заглушка нейросети для проверки работы сервера

def get_neuromethods():
    #получаем список методов
    try:
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("select \"method_name\" from portfolio_neuromethods")
        rows = cur.fetchall()
        con.close()
        result = []
        for i in range(len(rows)):
            result.append(rows[i][0])
        return result

    except:
        return 'Не получилось загрузить названия алгоритмов нейросети'

def generate_prediction(algoritms):
    #генерируем случайные прогнозы для двух методов
    result = []
    if randint(1, 2) == 1:
        result.append(algoritms[0] + " +")
        result.append(algoritms[1] + " +")
    else:
        result.append(algoritms[0] + " -")
        result.append(algoritms[1] + " -")
    x = randint(1, 10) * 10
    y = 0
    z = randint(1, 2)
    if z == 1:
        y = x - z * 10
    else:
        y = x + z * 10
    result[0] += str(x) + '%'
    result[1] += str(y) + '%'
    return result[0] + ' ' + result[1] #прогноз из двух методов
    
def get_datetime_news(news_text):
    #получаем дату выхода новости
    try:
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("select \"date\" from news_news WHERE header = \'" + news_text + "\'")
        rows = cur.fetchall()
        con.close()
        return rows[0][0]

    except:
        return 'Не получилось загрузить дату выхода новости'

def add_one_hour(time_start):
    #добавляем ко времени в формате datetime 1 час
    mas = time_start.split(' ')
    mas[1] = mas[1].split(':')
    mas[1][0] = str(int(mas[1][0]) + 1)
    time_stop = ''
    time_stop += ':'.join(list(map(str, mas[1])))
    time_stop = mas[0] + ' ' + time_stop
    time_stop = time_stop.split('+')
    return time_stop[0]

def write_db(ticker, company_name, time_release, time_stop, source, header, annotation, prediction):
    #добавляем данные в бд
    try:
        con = get_db_connection()
        cur = con.cursor()
       
        stroka = "insert into predictions_companypredictions (ticker, company_name, time_release, time_stop, source, header, annotation, prediction) values (\'" + ticker + "\', \'" + \
                     company_name + "\', \'" + str(time_release) + "\', \'" + time_stop + \
                         "\', \'" + source + "\',\'" + header + "\',\'" + annotation + \
                             "\',\'" + prediction + "\')"
                     
        
        
        cur.execute(stroka)

        con.commit()  

        con.close()
    except:
        print('ошибка при добавлении в базу данных прогноза')
        con.close()

def main(news_text, annotation, company_name, ticker, source):
    algoritms = get_neuromethods() #получаем список алгоритмов из таблицы
    prediction = generate_prediction(algoritms) #состаляем прогноз

    #тикер, название компании, время выхода, время остановки, источник, заголовок, аннотация, прогноз
    time_release = get_datetime_news(news_text)
    print(time_release)
    
    time_stop = add_one_hour(str(time_release)) #прибавляем 1 час ко времени окончания прогноза
    
    write_db(ticker, company_name, time_release, time_stop, source, news_text, annotation, prediction)
    print('добавлена новая строка прогноза')
    

    


    
    
    
    