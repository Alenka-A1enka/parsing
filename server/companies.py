from db_connection import get_db_connection
from neural_network import main as neural_network_main

#модуль, который отправляет id компании из таблицы companies из бд (получаем текст новости и ее аннотацию)

#подгружаем данные обо всех компаниях: название и тикер (не будет автоматического обновления списка, так как добавляются данные редко)
def get_companies_information_from_bd():
    try:
        con = get_db_connection()
        cur = con.cursor()  
        cur.execute("select id, ticker, company_name from portfolio_companies")
        rows = cur.fetchall()
        con.close()
        return rows
        
    except:
        return ''

def get_id_company_from_news(news_text, news_annotation, companies_data):
    #объединяем все в одну строку
    text = ' '+ news_text + " " + news_annotation
    for index, ticker, comp_name in companies_data:
        #варианты тикера (так как тикер очень короткий и его случайно можно взять из середины слова)
        ticker1 = ' ' + ticker + ' '
        ticker2 = ' ' + ticker + ','
        ticker3 = ' ' + ticker + '.'
        
        #поиск тикеров и названий
        i1 = text.find(ticker1)
        i2 = text.find(ticker2)
        i3 = text.find(ticker3)
        j = text.find(comp_name)
        
        #если хотя бы один индекс не равен -1
        if(i1 != -1 or i2 != -1 or i3 != -1 or j != -1):
            return [comp_name, ticker]
    return ''
    
def get_index_from_bd(news_text):
    #получаем индекс новости
    try:
        con = get_db_connection()
        cur = con.cursor()

        cur.execute("select \"id\" from news_news WHERE header = \'" + news_text + "\'")
        rows = cur.fetchall()

        con.close()
        
        return rows[0][0]
        
    except:
        print('error to ge index (companies)')
        con.close()
        
        
def write_to_bd(company_name, index):
    #дозапись прогноза в бд в строку с новостью 
    try:
        con = get_db_connection()
        cur = con.cursor()

        stroka = "update news_news set company_name = \'" + company_name + "\' where id = " + str(index)

        cur.execute(stroka)
        
        con.commit()

        con.close()
    except:
        print('error to write data to bd (companies)')
        con.close()

#загрузка из бд
companies_data = get_companies_information_from_bd()


def main(news_text, annotation, source):
    #получаем название компании
    company_name, ticker = get_id_company_from_news(news_text, 
                            annotation, 
                            companies_data)
    if company_name != '':
        index = get_index_from_bd(news_text) #ищем индекс новости
        write_to_bd(company_name, index) #записываем название компании в базу
        
        #вызываем нейросеть
        neural_network_main(news_text, annotation, company_name, ticker, source)
        
        
    else: 
        print('not such company name')
    



