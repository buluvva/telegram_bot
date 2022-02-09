import pandas as pd
import datetime
import pygsheets as pg
import dateutil
from url import url_table
scope = ["https://spreadsheets.google.com/feeds",
         'https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive.file',
         'https://www.googleapis.com/auth/drive']
c = pg.authorize(client_secret='client_secret.json',
                 service_account_file='service_file.json',
                 service_account_env_var=None,
                 credentials_directory=None,
                 scopes=scope,
                 custom_credentials=None,
                 local=False)


def grabber(url):
    sheet = c.open_by_url(url)
    wks = sheet.worksheet('title', 'Лист1')
    data = wks.get_as_df()
    return data

def prog(file):

    data_salary = pd.read_excel(file)
    data_table = grabber(url_table)
    name = data_table.loc[:, 'Фамилия'] + ' ' + data_table.loc[:, 'Имя']

    # Заполняем столбцы 'Зарплата в месяц', 'НДФЛ в год', 'Годовой доход-НДФЛ' и 'Годовой доход'

    for i in range(len(data_salary)):
        for row in range(len(name)):
            if data_salary.loc[i, 'Имя'] == name[row]:
                data_table.loc[row, 'Зарплата в месяц'] = data_salary.loc[i, 'Доход']
                data_table.loc[row, 'Годовой доход'] = data_salary.loc[i, 'Доход']*12
                data_table.loc[row, 'Годовой доход-НДФЛ'] = data_salary.loc[i, 'Доход'] * 12*0.87
                data_table.loc[row, 'НДФЛ в год'] = data_salary.loc[i, 'Доход'] * 12 * 0.13
    # Заполняем столбец 'ФИО'
    name = name + ' ' + data_table.loc[:, 'Отчество']
    for row in range(data_table.shape[0]):
        data_table.loc[row, 'ФИО'] = name[row]
    # Заполняем столбец 'Младше 30?'
    now = datetime.datetime.utcnow()
    now = now.date()
    for row in range(len(data_table)):
        data_table.loc[row, 'Дата рождения'] = pd.to_datetime(data_table.loc[row, 'Дата рождения'], errors="coerce")
        data_table.loc[row, 'Младше 30?'] = \
            dateutil.relativedelta.relativedelta(now, data_table.loc[row, 'Дата рождения'])
        data_table.loc[row, 'Возраст,лет'] = data_table.loc[row, 'Младше 30?'].years
        if data_table.loc[row, 'Возраст,лет'] < 30:
            data_table.loc[row, 'Младше 30?'] = 'Да'
        else:
            data_table.loc[row, 'Младше 30?'] = 'Нет'
    # Заполняем пустые ячейки
    for i in range(len(data_table)):
        for row in range(len(data_table)):
            if data_table.iloc[i, row] == '':
                data_table.iloc[i, row] = '-'
    data_table.to_excel('result.xlsx', index=False)
